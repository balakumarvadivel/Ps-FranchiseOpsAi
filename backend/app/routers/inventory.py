from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.inventory import Inventory, Product
from app.models.sales import Sale
from app.schemas.inventory import InventoryOut, InventoryUpdate, ProductCreate, ProductOut
from app.services.ai.recommender import recommend_for_inventory, recommend_stock_transfer

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


def _recompute_status(quantity: int, reorder_level: int) -> str:
    if quantity <= 0:
        return "out_of_stock"
    if quantity <= reorder_level:
        return "low_stock"
    if quantity > reorder_level * 5:
        return "overstock"
    return "in_stock"


@router.get("", response_model=list[InventoryOut])
def list_inventory(
    outlet_id: Optional[int] = None,
    warehouse_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Inventory).join(Product, Product.id == Inventory.product_id)
    if allowed is not None:
        query = query.filter(Inventory.outlet_id.in_(allowed))
    if outlet_id:
        query = query.filter(Inventory.outlet_id == outlet_id)
    if warehouse_status:
        query = query.filter(Inventory.warehouse_status == warehouse_status)

    rows = query.all()
    return [
        InventoryOut(
            id=r.id, outlet_id=r.outlet_id, product_id=r.product_id, quantity=r.quantity,
            warehouse_status=r.warehouse_status, last_restocked=r.last_restocked,
            reorder_level=r.product.reorder_level, product_name=r.product.name,
        )
        for r in rows
    ]


@router.put("/{inventory_id}/stock", response_model=InventoryOut)
def update_stock(inventory_id: int, payload: InventoryUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    row = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Inventory record not found")

    allowed = scoped_outlet_ids(current_user)
    if allowed is not None and row.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    row.quantity = payload.quantity
    row.warehouse_status = _recompute_status(payload.quantity, row.product.reorder_level)
    db.commit()
    db.refresh(row)
    return InventoryOut(
        id=row.id, outlet_id=row.outlet_id, product_id=row.product_id, quantity=row.quantity,
        warehouse_status=row.warehouse_status, last_restocked=row.last_restocked,
        reorder_level=row.product.reorder_level, product_name=row.product.name,
    )


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "SKU already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/alerts/reorder")
def reorder_recommendations(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    """AI feature: 'Recommend reorder quantity' — flags SKUs at/below reorder level."""
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Inventory).join(Product, Product.id == Inventory.product_id)
    if allowed is not None:
        query = query.filter(Inventory.outlet_id.in_(allowed))
    if outlet_id:
        query = query.filter(Inventory.outlet_id == outlet_id)

    since = date.today() - timedelta(days=30)
    recommendations = []
    for row in query.all():
        avg_daily_sales = (
            db.query(func.coalesce(func.sum(Sale.quantity), 0))
            .filter(Sale.product_id == row.product_id, Sale.outlet_id == row.outlet_id, Sale.sale_date >= since)
            .scalar() or 0
        ) / 30

        rec = recommend_for_inventory(
            outlet_name=row.outlet.name, outlet_id=row.outlet_id, product_name=row.product.name,
            quantity=row.quantity, reorder_level=row.product.reorder_level, avg_daily_sales=avg_daily_sales,
        )
        if rec:
            recommendations.append(rec)

    return sorted(recommendations, key=lambda r: r.priority)


@router.get("/alerts/transfer-suggestions")
def transfer_suggestions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    AI feature: 'Suggest outlet-to-outlet stock transfer'. For each product,
    matches an overstocked outlet against an understocked one.
    """
    rows = db.query(Inventory).join(Product, Product.id == Inventory.product_id).all()
    by_product: dict[int, list] = {}
    for r in rows:
        by_product.setdefault(r.product_id, []).append(r)

    suggestions = []
    for product_id, entries in by_product.items():
        overstocked = [e for e in entries if e.warehouse_status == "overstock"]
        understocked = [e for e in entries if e.warehouse_status in ("low_stock", "out_of_stock")]
        for over in overstocked:
            for under in understocked:
                surplus = over.quantity - (over.product.reorder_level * 2)
                shortage = max(1, under.product.reorder_level - under.quantity)
                if surplus > 0:
                    suggestions.append(recommend_stock_transfer(
                        from_outlet=over.outlet.name, to_outlet=under.outlet.name,
                        product_name=over.product.name, surplus_qty=surplus, shortage_qty=shortage,
                    ))
    return suggestions
