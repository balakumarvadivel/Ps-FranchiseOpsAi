from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.database import get_db
from app.models.user import User, Outlet
from app.models.sales import Sale
from app.schemas.outlet import OutletCreate, OutletUpdate, OutletOut, OutletKPI
from app.services.ai.health_score import compute_outlet_health_score
from app.services import outlet_service

router = APIRouter(prefix="/api/v1/outlets", tags=["Outlets"])


@router.get("", response_model=list[OutletOut])
def list_outlets(
    region: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Outlet)
    if allowed is not None:
        query = query.filter(Outlet.id.in_(allowed))
    if region:
        query = query.filter(Outlet.region == region)
    if status_filter:
        query = query.filter(Outlet.status == status_filter)
    return query.order_by(Outlet.name).all()


@router.get("/{outlet_id}", response_model=OutletOut)
def get_outlet(outlet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    outlet = outlet_service.get_outlet_or_404(db, outlet_id, current_user)
    return outlet


@router.post("", response_model=OutletOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager"))])
def create_outlet(payload: OutletCreate, db: Session = Depends(get_db)):
    if db.query(Outlet).filter(Outlet.code == payload.code).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Outlet code already exists")
    outlet = Outlet(**payload.model_dump())
    db.add(outlet)
    db.commit()
    db.refresh(outlet)
    return outlet


@router.put("/{outlet_id}", response_model=OutletOut,
            dependencies=[Depends(require_role("admin", "regional_manager"))])
def update_outlet(outlet_id: int, payload: OutletUpdate, db: Session = Depends(get_db)):
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Outlet not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(outlet, field, value)
    db.commit()
    db.refresh(outlet)
    return outlet


@router.delete("/{outlet_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_role("admin"))])
def delete_outlet(outlet_id: int, db: Session = Depends(get_db)):
    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Outlet not found")
    db.delete(outlet)
    db.commit()


@router.get("/kpi/ranking", response_model=list[OutletKPI])
def outlet_ranking(
    days: int = Query(30, ge=1, le=365, description="Rolling window size, in days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Core of the Outlet Performance Agent: revenue, growth % (this window vs the
    previous equal window) and a composite health score, per outlet.
    """
    allowed = scoped_outlet_ids(current_user)
    outlets_q = db.query(Outlet)
    if allowed is not None:
        outlets_q = outlets_q.filter(Outlet.id.in_(allowed))
    outlets = outlets_q.all()

    window_end = date.today()
    window_start = window_end - timedelta(days=days)
    prev_start = window_start - timedelta(days=days)

    results = []
    for outlet in outlets:
        current_revenue, current_orders = outlet_service.revenue_and_orders(db, outlet.id, window_start, window_end)
        prev_revenue, _ = outlet_service.revenue_and_orders(db, outlet.id, prev_start, window_start)

        growth = 0.0
        if prev_revenue > 0:
            growth = round(((current_revenue - prev_revenue) / prev_revenue) * 100, 2)

        health = compute_outlet_health_score(db, outlet.id)
        status_label = "Healthy" if health >= 75 else "Average" if health >= 50 else "Critical"

        results.append(OutletKPI(
            outlet_id=outlet.id, name=outlet.name, revenue=current_revenue,
            orders=current_orders, growth_percent=growth, health_score=health,
            status=status_label,
        ))

    return sorted(results, key=lambda r: r.revenue, reverse=True)
