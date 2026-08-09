from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(..., description="admin | regional_manager | outlet_manager")
    outlet_id: Optional[int] = None
    region: Optional[str] = Field(None, description="Required for regional_manager role")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    outlet_id: Optional[int] = None
    region: Optional[str] = None

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()
