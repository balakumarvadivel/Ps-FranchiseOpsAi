from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class SaleCreate(BaseModel):
    outlet_id: int
    product_id: int
    customer_id: Optional[int] = None
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount: float = 0
    sale_date: Optional[datetime] = None

    @field_validator("discount")
    @classmethod
    def discount_not_negative(cls, v):
        if v < 0:
            raise ValueError("discount cannot be negative")
        return v


class SaleOut(BaseModel):
    id: int
    outlet_id: int
    product_id: int
    customer_id: Optional[int]
    quantity: int
    unit_price: float
    total_amount: float
    discount: float
    sale_date: datetime

    class Config:
        from_attributes = True


class SalesTrendPoint(BaseModel):
    label: str
    revenue: float
    orders: int
