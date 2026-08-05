from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.database import get_db
from app.models.user import User, Outlet
from app.models.sales import Sale
from app.models.marketing_audit import Audit
from app.models.ai import Recommendation
from app.schemas.recommendations import RecommendationOut, RecommendationStatusUpdate
from app.services.ai.health_score import compute_outlet_health_score
from app.services.ai.recommender import recommend_for_outlet, recommend_audit
from app.services.inventory_recommendations import inventory_recommendation_objects

router = APIRouter(prefix="/api/v1/recommendations", tags=["Business Recommendation Engine"])


@router.get("", response_model=list[RecommendationOut])
def list_recommendations(
    priority: Optional[str] = None,
    status_filter: Optional[str] = None,
    outlet_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Recommendation)
    if allowed is not None:
        query = query.filter(Recommendation.outlet_id.in_(allowed) | Recommendation.outlet_id.is_(None))
    if priority:
        query = query.filter(Recommendation.priority == priority)
    if status_filter:
        query = query.filter(Recommendation.status == status_filter)
    if outlet_id:
        query = query.filter(Recommendation.outlet_id == outlet_id)

    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    rows = query.all()
    return sorted(rows, key=lambda r: priority_rank.get(r.priority, 9))


@router.put("/{recommendation_id}/status", response_model=RecommendationOut)
def update_recommendation_status(recommendation_id: int, payload: RecommendationStatusUpdate,
                                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Recommendation not found")
    if payload.status not in ("open", "in_progress", "resolved", "dismissed"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid status value")
    rec.status = payload.status
    db.commit()
    db.refresh(rec)
    return rec


@router.post("/refresh", dependencies=[Depends(require_role("admin", "regional_manager"))])
def refresh_recommendations(db: Session = Depends(get_db)):
    """
    Re-runs the recommendation engine across outlets, inventory, staff and
    audits, and persists fresh rows. Existing 'open' recommendations are
    cleared first so this stays idempotent rather than accumulating
    duplicates every time it's run (e.g. from a daily scheduled job).
    """
    db.query(Recommendation).filter(Recommendation.status == "open").delete()

    today = date.today()
    window_start = today - timedelta(days=30)
    prev_start = window_start - timedelta(days=30)

    new_recs = []

    for outlet in db.query(Outlet).all():
        health = compute_outlet_health_score(db, outlet.id)

        current = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.outlet_id == outlet.id, Sale.sale_date >= window_start).scalar()
        previous = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.outlet_id == outlet.id, Sale.sale_date >= prev_start, Sale.sale_date < window_start).scalar()
        current, previous = float(current), float(previous)
        growth = round(((current - previous) / previous) * 100, 2) if previous else 0.0

        new_recs.extend(recommend_for_outlet(outlet.name, outlet.id, health, growth))

        overdue_audit = db.query(Audit).filter(
            Audit.outlet_id == outlet.id, Audit.status != "completed", Audit.scheduled_date < today,
        ).order_by(Audit.scheduled_date).first()
        if overdue_audit:
            days_overdue = (today - overdue_audit.scheduled_date).days
            new_recs.append(recommend_audit(outlet.name, outlet.id, days_overdue))

    new_recs.extend(inventory_recommendation_objects(db))

    for rec in new_recs:
        db.add(Recommendation(
            outlet_id=rec.outlet_id, title=rec.title, description=rec.description,
            priority=rec.priority, category=rec.category, status="open",
        ))
    db.commit()

    return {"message": f"{len(new_recs)} recommendation(s) generated."}
