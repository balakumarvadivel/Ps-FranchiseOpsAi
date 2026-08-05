from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RecommendationOut(BaseModel):
    id: int
    outlet_id: Optional[int]
    title: str
    description: Optional[str]
    priority: str
    category: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationStatusUpdate(BaseModel):
    status: str  # open | in_progress | resolved | dismissed
