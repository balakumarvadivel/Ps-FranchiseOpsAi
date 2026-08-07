from pydantic import BaseModel


class PermissionOut(BaseModel):
    id: int
    code: str
    description: str | None = None

    class Config:
        from_attributes = True


class RolePermissionMatrix(BaseModel):
    role: str
    permissions: list[str]


class RolePermissionUpdate(BaseModel):
    permission_codes: list[str]
