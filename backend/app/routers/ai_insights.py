from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, scoped_outlet_ids
from app.database import get_db
from app.models.user import User, Outlet
from app.models.sales import Sale
from app.models.marketing_audit import Audit
from app.services.ai.health_score import compute_outlet_health_score, compute_outlet_health_breakdown
from app.services.ai.forecasting import linear_regression_forecast
from app.services.ai.recommender import recommend_for_outlet, recommend_audit
from app.services.ai.nlg_summary import generate_executive_summary

router = APIRouter(prefix="/api/v1/ai", tags=["AI Insights"])


@router.get("/outlets/{outlet_id}/health-score")
def outlet_health_score(outlet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Outlet not found")
    return compute_outlet_health_breakdown(db, outlet_id)


@router.get("/forecast/revenue")
def forecast_revenue(
    outlet_id: int | None = None,
    range: str = Query("30D", pattern="^(7D|30D|90D)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI feature: Revenue Forecasting. Builds a daily history then projects forward."""
    allowed = scoped_outlet_ids(current_user)
    if outlet_id and allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    history_days = {"7D": 30, "30D": 90, "90D": 180}[range]
    periods_ahead = {"7D": 7, "30D": 30, "90D": 90}[range]
    since = date.today() - timedelta(days=history_days)

    query = db.query(
        func.date_trunc("day", Sale.sale_date).label("day"),
        func.sum(Sale.total_amount).label("revenue"),
    ).filter(Sale.sale_date >= since)

    if allowed is not None:
        query = query.filter(Sale.outlet_id.in_(allowed))
    if outlet_id:
        query = query.filter(Sale.outlet_id == outlet_id)

    rows = query.group_by("day").order_by("day").all()
    history = [float(r.revenue) for r in rows]

    if not history:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not enough sales history to forecast")

    result = linear_regression_forecast(history, periods_ahead)
    result["range"] = range
    result["history_points"] = len(history)
    return result


@router.get("/recommendations")
def generate_recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Business Recommendation Engine: pulls health scores + growth + overdue
    audits across all outlets in scope and returns prioritized recommendations.
    """
    allowed = scoped_outlet_ids(current_user)
    outlets_q = db.query(Outlet)
    if allowed is not None:
        outlets_q = outlets_q.filter(Outlet.id.in_(allowed))
    outlets = outlets_q.all()

    recs = []
    today = date.today()
    for outlet in outlets:
        health = compute_outlet_health_score(db, outlet.id)

        window_start = today - timedelta(days=30)
        prev_start = window_start - timedelta(days=30)
        current = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.outlet_id == outlet.id, Sale.sale_date >= window_start).scalar()
        previous = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.outlet_id == outlet.id, Sale.sale_date >= prev_start, Sale.sale_date < window_start).scalar()
        current, previous = float(current), float(previous)
        growth = round(((current - previous) / previous) * 100, 2) if previous else 0.0

        recs.extend(recommend_for_outlet(outlet.name, outlet.id, health, growth))

        overdue_audit = db.query(Audit).filter(
            Audit.outlet_id == outlet.id, Audit.status != "completed",
            Audit.scheduled_date < today,
        ).order_by(Audit.scheduled_date).first()
        if overdue_audit:
            days_overdue = (today - overdue_audit.scheduled_date).days
            recs.append(recommend_audit(outlet.name, outlet.id, days_overdue))

    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recs.sort(key=lambda r: priority_rank.get(r.priority, 9))
    return recs


@router.get("/executive-summary")
def executive_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Franchise Intelligence Engine: cross-domain roll-up + NLG summary."""
    allowed = scoped_outlet_ids(current_user)
    outlets_q = db.query(Outlet)
    if allowed is not None:
        outlets_q = outlets_q.filter(Outlet.id.in_(allowed))
    outlets = outlets_q.all()
    if not outlets:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No outlets in scope")

    today = date.today()
    window_start = today - timedelta(days=30)
    prev_start = window_start - timedelta(days=30)

    outlet_ids = [o.id for o in outlets]
    current_rev = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.outlet_id.in_(outlet_ids), Sale.sale_date >= window_start).scalar()
    prev_rev = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.outlet_id.in_(outlet_ids), Sale.sale_date >= prev_start, Sale.sale_date < window_start).scalar()
    current_rev, prev_rev = float(current_rev), float(prev_rev)
    revenue_growth = round(((current_rev - prev_rev) / prev_rev) * 100, 2) if prev_rev else 0.0

    scored = [(o, compute_outlet_health_score(db, o.id)) for o in outlets]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    best_outlet, best_health = scored[0]
    worst_outlet, worst_health = scored[-1]

    critical_count = sum(1 for _, h in scored if h < 50)
    overall_health = round(sum(h for _, h in scored) / len(scored), 1)

    summary_text = generate_executive_summary(
        total_revenue=current_rev,
        revenue_growth_percent=revenue_growth,
        overall_health_score=overall_health,
        best_outlet_name=best_outlet.name,
        best_outlet_growth=best_health,   # health used as a stand-in trend indicator for the best outlet
        worst_outlet_name=worst_outlet.name,
        worst_outlet_health=worst_health,
        profit_margin_percent=22.0,        # replace with a real aggregate once cost data is populated
        critical_outlet_count=critical_count,
    )

    return {
        "summary": summary_text,
        "total_revenue": current_rev,
        "revenue_growth_percent": revenue_growth,
        "overall_health_score": overall_health,
        "best_outlet": {"id": best_outlet.id, "name": best_outlet.name, "health_score": best_health},
        "worst_outlet": {"id": worst_outlet.id, "name": worst_outlet.name, "health_score": worst_health},
        "critical_outlet_count": critical_count,
    }
