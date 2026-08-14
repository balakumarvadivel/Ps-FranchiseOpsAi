import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import hash_password, verify_password, create_access_token, hash_reset_token
from app.core.rate_limit import login_rate_limit, register_rate_limit, forgot_password_rate_limit
from app.database import get_db
from app.models.user import User, Role, Region
from app.schemas.auth import (
    RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest,
    TokenResponse, UserOut,
)
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def _user_to_out(user: User) -> UserOut:
    return UserOut(
        id=user.id, full_name=user.full_name, email=user.email,
        role=user.role.name, outlet_id=user.outlet_id, region=user.region,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(register_rate_limit)])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")

    role = db.query(Role).filter(Role.name == payload.role).first()
    if not role:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown role '{payload.role}'")

    if payload.role == "outlet_manager" and not payload.outlet_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "outlet_id is required for outlet_manager role")

    if payload.role == "regional_manager":
        if not payload.region:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "region is required for regional_manager role")
        if not db.query(Region).filter(Region.name == payload.region).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown region '{payload.region}'")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=role.id,
        outlet_id=payload.outlet_id if payload.role == "outlet_manager" else None,
        region=payload.region if payload.role == "regional_manager" else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": role.name})
    return TokenResponse(access_token=token, user=_user_to_out(user))


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(login_rate_limit)])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Note: uses OAuth2PasswordRequestForm (username + password fields) so this
    endpoint works directly with FastAPI's Swagger 'Authorize' button. The
    frontend can send `username` = email in a standard form-encoded POST,
    or use the JSON `LoginRequest` shape via /login-json below.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")

    token = create_access_token({"user_id": user.id, "role": user.role.name})
    return TokenResponse(access_token=token, user=_user_to_out(user))


@router.post("/login-json", response_model=TokenResponse, dependencies=[Depends(login_rate_limit)])
def login_json(payload: LoginRequest, db: Session = Depends(get_db)):
    """JSON-friendly login for the React frontend (axios POST with JSON body)."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")

    token = create_access_token({"user_id": user.id, "role": user.role.name})
    return TokenResponse(access_token=token, user=_user_to_out(user))


@router.post("/forgot-password", dependencies=[Depends(forgot_password_rate_limit)])
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Always return a generic message — never reveal whether the email exists.
    generic_response = {"message": "If that email exists, a reset link has been sent."}
    if not user:
        return generic_response

    raw_token = secrets.token_urlsafe(32)
    user.reset_token_hash = hash_reset_token(raw_token)
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.commit()

    emailed = send_password_reset_email(user.email, raw_token)
    if emailed:
        # Real email was sent — never leak the token in the API response too.
        return generic_response

    # SMTP isn't configured in this environment — fall back to returning the
    # raw token directly so the flow is still testable end-to-end without a
    # mail account. Clearly marked as a dev-only shortcut, not something to
    # ship with SMTP unconfigured in a real deployment.
    return {**generic_response, "dev_reset_token": raw_token}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_reset_token(payload.token)
    user = db.query(User).filter(User.reset_token_hash == token_hash).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")

    user.hashed_password = hash_password(payload.new_password)
    user.reset_token_hash = None
    user.reset_token_expires = None
    db.commit()
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return _user_to_out(current_user)
