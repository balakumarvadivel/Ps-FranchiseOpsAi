from typing import Optional
from pydantic import BaseModel, EmailStr


class UserAdminOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    outlet_id: Optional[int]
    region: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class UserAdminUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    outlet_id: Optional[int] = None
    region: Optional[str] = None
    is_active: Optional[bool] = None
