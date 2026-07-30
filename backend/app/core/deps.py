from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "user_id" not in payload:
        raise credentials_error

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if user is None or not user.is_active:
        raise credentials_error
    return user


def require_role(*allowed_roles: str):
    """Usage: Depends(require_role('admin', 'regional_manager'))"""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


def scoped_outlet_ids(current_user: User) -> list[int] | None:
    """
    Returns the list of outlet_ids the current user is allowed to see, or
    None if they have network-wide access (admin / regional_manager).
    Outlet managers are restricted to their own outlet.
    """
    if current_user.role.name == "outlet_manager":
        return [current_user.outlet_id] if current_user.outlet_id else []
    return None
