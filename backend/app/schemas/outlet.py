from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class OutletBase(BaseModel):
    name: str = Field(..., max_length=150)
    code: str = Field(..., max_length=20)
    city: str
    state: str
    region: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opened_on: Optional[date] = None
    status: str = "active"


class OutletCreate(OutletBase):
    pass


class OutletUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None


class OutletOut(OutletBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OutletKPI(BaseModel):
    outlet_id: int
    name: str
    revenue: float
    orders: int
    growth_percent: float
    health_score: float
    status: str  # Healthy | Average | Critical
