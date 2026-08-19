from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    outlet_id: Optional[int] = None
    name: str
    channel: str = Field(..., pattern="^(social|print|in-store|email)$")
    campaign_type: str = Field("promotional", pattern="^(promotional|seasonal|loyalty|launch)$")
    start_date: date
    end_date: Optional[date] = None
    budget: float = Field(..., gt=0)
    ad_cost: float = 0
    customer_reach: int = 0
    leads: int = 0
    coupon_code: Optional[str] = None


class CampaignUpdate(BaseModel):
    revenue_generated: Optional[float] = None
    coupon_redemptions: Optional[int] = None
    conversions: Optional[int] = None
    status: Optional[str] = None


class CampaignOut(BaseModel):
    id: int
    outlet_id: Optional[int]
    name: str
    channel: str
    campaign_type: Optional[str] = None
    start_date: date
    end_date: Optional[date]
    budget: float
    ad_cost: float
    revenue_generated: float
    customer_reach: int
    leads: int = 0
    conversions: int = 0
    conversion_rate_percent: float = 0
    coupon_redemptions: int
    status: str
    roi_percent: float

    class Config:
        from_attributes = True


class CustomerSegment(BaseModel):
    segment: str  # VIP | Regular | At-risk | New
    customer_count: int
    avg_spend: float
