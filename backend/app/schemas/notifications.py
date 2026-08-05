from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    title: str
    message: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: int
    outlet_id: Optional[int]
    type: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
