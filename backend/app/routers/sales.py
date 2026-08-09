from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.sales import Sale
from app.models.inventory import Product
from app.schemas.sales import SaleCreate, SaleOut, SalesTrendPoint

router = APIRouter(prefix="/api/v1/sales", tags=["Sales"])


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def record_sale(payload: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and payload.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")

    total = (payload.unit_price * payload.quantity) - payload.discount
    if total < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Discount exceeds sale total")

    sale = Sale(
        outlet_id=payload.outlet_id,
        product_id=payload.product_id,
        customer_id=payload.customer_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        discount=payload.discount,
        total_amount=total,
        sale_date=payload.sale_date or datetime.utcnow(),
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.get("", response_model=list[SaleOut])
def list_sales(
    outlet_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(Sale)
    if allowed is not None:
        query = query.filter(Sale.outlet_id.in_(allowed))
    if outlet_id:
        if allowed is not None and outlet_id not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")
        query = query.filter(Sale.outlet_id == outlet_id)
    if date_from:
        query = query.filter(Sale.sale_date >= date_from)
    if date_to:
        query = query.filter(Sale.sale_date <= date_to)

    return (
        query.order_by(Sale.sale_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


@router.get("/trend", response_model=list[SalesTrendPoint])
def sales_trend(
    outlet_id: Optional[int] = None,
    period: str = Query("Monthly", pattern="^(Daily|Weekly|Monthly|Yearly)$"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Powers the Daily/Weekly/Monthly/Yearly sales performance chart. Pass date_from/date_to to override the default lookback window."""
    allowed = scoped_outlet_ids(current_user, db)
    if outlet_id and allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    bucket_expr = {
        "Daily": func.date_trunc("day", Sale.sale_date),
        "Weekly": func.date_trunc("week", Sale.sale_date),
        "Monthly": func.date_trunc("month", Sale.sale_date),
        "Yearly": func.date_trunc("year", Sale.sale_date),
    }[period]

    lookback = {"Daily": 30, "Weekly": 90, "Monthly": 365, "Yearly": 365 * 5}[period]
    since = date_from or (date.today() - timedelta(days=lookback))

    query = db.query(
        bucket_expr.label("bucket"),
        func.sum(Sale.total_amount).label("revenue"),
        func.count(Sale.id).label("orders"),
    ).filter(Sale.sale_date >= since)

    if date_to:
        query = query.filter(Sale.sale_date <= date_to)
    if allowed is not None:
        query = query.filter(Sale.outlet_id.in_(allowed))
    if outlet_id:
        query = query.filter(Sale.outlet_id == outlet_id)

    rows = query.group_by("bucket").order_by("bucket").all()
    return [
        SalesTrendPoint(label=row.bucket.strftime("%d %b %Y"), revenue=float(row.revenue), orders=row.orders)
        for row in rows
    ]


@router.get("/category-performance")
def category_performance(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """Revenue and units sold by product category — powers the Category Performance chart."""
    allowed = scoped_outlet_ids(current_user, db)
    since = date.today() - timedelta(days=days)

    query = (
        db.query(
            Product.category.label("category"),
            func.sum(Sale.total_amount).label("revenue"),
            func.sum(Sale.quantity).label("units"),
        )
        .join(Product, Product.id == Sale.product_id)
        .filter(Sale.sale_date >= since)
    )
    if allowed is not None:
        query = query.filter(Sale.outlet_id.in_(allowed))

    rows = query.group_by(Product.category).order_by(func.sum(Sale.total_amount).desc()).all()
    return [{"category": r.category, "revenue": float(r.revenue or 0), "units": int(r.units or 0)} for r in rows]
