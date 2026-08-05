from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    report_type: str = Field(..., pattern="^(sales|inventory|staff|marketing|audit|overall)$")
    format: str = Field(..., pattern="^(pdf|excel|csv)$")
    outlet_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class ReportOut(BaseModel):
    id: int
    report_type: str
    format: str
    file_path: Optional[str]
    date_from: Optional[date]
    date_to: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True
