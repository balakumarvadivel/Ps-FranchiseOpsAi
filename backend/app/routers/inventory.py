from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.inventory import Inventory, Product, Supplier, InventoryBatch
from app.models.sales import Sale
from app.schemas.inventory import (
    InventoryOut, InventoryUpdate, ProductCreate, ProductOut,
    SupplierCreate, SupplierOut, BatchCreate, BatchOut,
)
from app.services.ai.recommender import recommend_stock_transfer
from app.services.inventory_recommendations import inventory_recommendation_objects

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
    if outlet_id and allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    recommendations = inventory_recommendation_objects(db, outlet_id)
    if allowed is not None:
        recommendations = [r for r in recommendations if r.outlet_id in allowed]

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


# --- Suppliers -------------------------------------------------------------
@router.get("/suppliers", response_model=list[SupplierOut])
def list_suppliers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Supplier).order_by(Supplier.name).all()


@router.post("/suppliers", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


# --- Batch / expiry tracking -------------------------------------------------------------
@router.post("/batches", response_model=BatchOut, status_code=status.HTTP_201_CREATED)
def create_batch(payload: BatchCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = db.query(Inventory).filter(Inventory.id == payload.inventory_id).first()
    if not inv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Inventory record not found")
    allowed = scoped_outlet_ids(current_user)
    if allowed is not None and inv.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    batch = InventoryBatch(**payload.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return BatchOut(
        id=batch.id, inventory_id=batch.inventory_id, batch_number=batch.batch_number,
        quantity=batch.quantity, manufactured_on=batch.manufactured_on, expiry_date=batch.expiry_date,
        product_name=inv.product.name, outlet_name=inv.outlet.name,
    )


@router.get("/batches", response_model=list[BatchOut])
def list_batches(
    outlet_id: Optional[int] = None,
    expiring_within_days: Optional[int] = Query(None, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI feature: Expiry Tracking / Expiry Prediction — list batches, optionally filtered to those expiring soon."""
    allowed = scoped_outlet_ids(current_user)
    query = db.query(InventoryBatch).join(Inventory, Inventory.id == InventoryBatch.inventory_id)
    if allowed is not None:
        query = query.filter(Inventory.outlet_id.in_(allowed))
    if outlet_id:
        query = query.filter(Inventory.outlet_id == outlet_id)
    if expiring_within_days is not None:
        cutoff = date.today() + timedelta(days=expiring_within_days)
        query = query.filter(InventoryBatch.expiry_date.isnot(None), InventoryBatch.expiry_date <= cutoff)

    rows = query.order_by(InventoryBatch.expiry_date).all()
    return [
        BatchOut(
            id=b.id, inventory_id=b.inventory_id, batch_number=b.batch_number, quantity=b.quantity,
            manufactured_on=b.manufactured_on, expiry_date=b.expiry_date,
            product_name=b.inventory.product.name, outlet_name=b.inventory.outlet.name,
        )
        for b in rows
    ]


# --- Inventory value & turnover -------------------------------------------------------------
@router.get("/value")
def inventory_value(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """
    Inventory Value + Inventory Turnover. Value = current stock valued at
    cost price. Turnover = (units sold in the last 90 days) / (average
    on-hand quantity) — a standard turnover approximation.
    """
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Inventory).join(Product, Product.id == Inventory.product_id)
    if allowed is not None:
        query = query.filter(Inventory.outlet_id.in_(allowed))
    if outlet_id:
        query = query.filter(Inventory.outlet_id == outlet_id)

    rows = query.all()
    total_value = sum(r.quantity * float(r.product.cost_price) for r in rows)
    total_units_on_hand = sum(r.quantity for r in rows)

    since = date.today() - timedelta(days=90)
    sales_query = db.query(func.coalesce(func.sum(Sale.quantity), 0)).filter(Sale.sale_date >= since)
    if allowed is not None:
        sales_query = sales_query.filter(Sale.outlet_id.in_(allowed))
    if outlet_id:
        sales_query = sales_query.filter(Sale.outlet_id == outlet_id)
    units_sold_90d = sales_query.scalar() or 0

    turnover = round(units_sold_90d / total_units_on_hand, 2) if total_units_on_hand else 0.0

    return {
        "total_inventory_value": round(total_value, 2),
        "total_units_on_hand": total_units_on_hand,
        "units_sold_last_90_days": int(units_sold_90d),
        "inventory_turnover_90d": turnover,
    }
