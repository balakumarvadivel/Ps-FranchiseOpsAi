from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    unit_price: float = Field(..., gt=0)
    cost_price: float = Field(..., gt=0)
    reorder_level: int = 20
    supplier_id: Optional[int] = None


class ProductOut(ProductCreate):
    id: int

    class Config:
        from_attributes = True


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


class InventoryOut(BaseModel):
    id: int
    outlet_id: int
    product_id: int
    quantity: int
    warehouse_status: str
    last_restocked: Optional[datetime]
    reorder_level: int
    product_name: str

    class Config:
        from_attributes = True


class BatchCreate(BaseModel):
    inventory_id: int
    batch_number: str
    quantity: int = Field(..., gt=0)
    manufactured_on: Optional[date] = None
    expiry_date: Optional[date] = None
