from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import scoped_outlet_ids
from app.models.user import Outlet, User
from app.models.sales import Sale


def get_outlet_or_404(db: Session, outlet_id: int, current_user: User) -> Outlet:
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    outlet = db.query(Outlet).filter(Outlet.id == outlet_id).first()
    if not outlet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Outlet not found")
    return outlet


def revenue_and_orders(db: Session, outlet_id: int, start: date, end: date) -> tuple[float, int]:
    row = (
        db.query(
            func.coalesce(func.sum(Sale.total_amount), 0),
            func.count(Sale.id),
        )
        .filter(Sale.outlet_id == outlet_id, Sale.sale_date >= start, Sale.sale_date < end)
        .first()
    )
    revenue, orders = row
    return float(revenue), int(orders)
