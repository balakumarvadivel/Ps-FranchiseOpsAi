from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.database import get_db
from app.models.user import User, Role
from app.schemas.user_admin import UserAdminOut, UserAdminUpdate

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])


def _to_out(user: User) -> UserAdminOut:
    return UserAdminOut(
        id=user.id, full_name=user.full_name, email=user.email,
        role=user.role.name, outlet_id=user.outlet_id, is_active=user.is_active,
    )


@router.get("", response_model=list[UserAdminOut],
            dependencies=[Depends(require_role("admin", "regional_manager"))])
def list_users(role: Optional[str] = None, outlet_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(User)
    if role:
        query = query.join(Role).filter(Role.name == role)
    if outlet_id:
        query = query.filter(User.outlet_id == outlet_id)
    return [_to_out(u) for u in query.order_by(User.full_name).all()]


@router.get("/{user_id}", response_model=UserAdminOut,
            dependencies=[Depends(require_role("admin", "regional_manager"))])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return _to_out(user)


@router.put("/{user_id}", response_model=UserAdminOut, dependencies=[Depends(require_role("admin"))])
def update_user(user_id: int, payload: UserAdminUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    data = payload.model_dump(exclude_unset=True)
    if "role" in data:
        role = db.query(Role).filter(Role.name == data["role"]).first()
        if not role:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown role '{data['role']}'")
        user.role_id = role.id
        data.pop("role")

    for field, value in data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return _to_out(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """Soft-delete: deactivates rather than hard-deletes, so audit/history stays intact."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.is_active = False
    db.commit()
