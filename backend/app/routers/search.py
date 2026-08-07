from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, scoped_outlet_ids
from app.database import get_db
from app.models.user import User, Outlet
from app.models.inventory import Product
from app.models.staff import Employee

router = APIRouter(prefix="/api/v1/search", tags=["Search"])


@router.get("")
def global_search(q: str = Query(..., min_length=2), db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    """
    Powers the navbar search box. Searches outlets (by name/city), products
    (by name/SKU), and employees (by name), scoped to what the current user
    is allowed to see. Returns a small, categorized result set rather than
    a paginated list — this is a quick-jump search, not a full search page.
    """
    allowed = scoped_outlet_ids(current_user)
    like = f"%{q}%"

    outlet_query = db.query(Outlet).filter(Outlet.name.ilike(like) | Outlet.city.ilike(like))
    if allowed is not None:
        outlet_query = outlet_query.filter(Outlet.id.in_(allowed))
    outlets = outlet_query.limit(5).all()

    products = db.query(Product).filter(Product.name.ilike(like) | Product.sku.ilike(like)).limit(5).all()

    employee_query = db.query(Employee).filter(Employee.full_name.ilike(like))
    if allowed is not None:
        employee_query = employee_query.filter(Employee.outlet_id.in_(allowed))
    employees = employee_query.limit(5).all()

    return {
        "outlets": [{"id": o.id, "name": o.name, "city": o.city, "type": "outlet"} for o in outlets],
        "products": [{"id": p.id, "name": p.name, "sku": p.sku, "type": "product"} for p in products],
        "employees": [{"id": e.id, "name": e.full_name, "outlet_id": e.outlet_id, "type": "employee"} for e in employees],
    }
