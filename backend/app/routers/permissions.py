from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role, get_current_user
from app.database import get_db
from app.models.user import Role, Permission, Region
from app.schemas.permissions import PermissionOut, RolePermissionMatrix, RolePermissionUpdate

router = APIRouter(prefix="/api/v1/permissions", tags=["Permissions & Regions"])


@router.get("", response_model=list[PermissionOut])
def list_permissions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Permission).order_by(Permission.code).all()


@router.get("/matrix", response_model=list[RolePermissionMatrix])
def role_permission_matrix(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """The full role -> permissions matrix, for the admin permissions UI."""
    roles = db.query(Role).order_by(Role.name).all()
    return [RolePermissionMatrix(role=r.name, permissions=[p.code for p in r.permissions]) for r in roles]


@router.put("/matrix/{role_name}", response_model=RolePermissionMatrix,
            dependencies=[Depends(require_role("admin"))])
def update_role_permissions(role_name: str, payload: RolePermissionUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Role '{role_name}' not found")

    permissions = db.query(Permission).filter(Permission.code.in_(payload.permission_codes)).all()
    found_codes = {p.code for p in permissions}
    missing = set(payload.permission_codes) - found_codes
    if missing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown permission code(s): {', '.join(missing)}")

    role.permissions = permissions
    db.commit()
    db.refresh(role)
    return RolePermissionMatrix(role=role.name, permissions=[p.code for p in role.permissions])


@router.get("/regions")
def list_regions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return [{"name": r.name, "description": r.description} for r in db.query(Region).order_by(Region.name).all()]
