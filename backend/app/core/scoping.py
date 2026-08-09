"""
Outlet-scoping registry
-------------------------
Single source of truth for which SQLAlchemy models represent outlet-owned
data. Both `apply_outlet_scope` (a small helper routers can use directly)
and `tests/test_query_scoping_guard.py` (a static-analysis regression test)
read from this same list, so there's exactly one place to update when a new
outlet-owned model is added — not one place to remember to update the
helper and a separate place to remember to update the test.
"""
from typing import Type

from sqlalchemy.orm import Query, Session

from app.models.sales import Sale, Customer
from app.models.inventory import Inventory
from app.models.staff import Employee
from app.models.marketing_audit import Audit, MarketingCampaign
from app.models.ai import Recommendation, Alert, AIInsight

# Every model with a direct outlet_id column. Order doesn't matter.
SCOPED_MODELS: dict[str, Type] = {
    "Sale": Sale,
    "Customer": Customer,
    "Inventory": Inventory,
    "Employee": Employee,
    "Audit": Audit,
    "MarketingCampaign": MarketingCampaign,
    "Recommendation": Recommendation,
    "Alert": Alert,
    "AIInsight": AIInsight,
}


def apply_outlet_scope(query: Query, model: Type, allowed_outlet_ids: list[int] | None) -> Query:
    """
    Applies outlet scoping to a query, if the model is registered as
    outlet-owned and the caller isn't unrestricted (allowed_outlet_ids is
    None means admin / no restriction).

    Models whose outlet_id is nullable (MarketingCampaign, Recommendation,
    Alert, AIInsight — NULL means "network-wide") keep NULL rows visible to
    everyone, matching the existing convention used across the routers.
    """
    if allowed_outlet_ids is None:
        return query
    if model not in SCOPED_MODELS.values():
        return query

    nullable_ok = model in (MarketingCampaign, Recommendation, Alert, AIInsight)
    if nullable_ok:
        return query.filter(model.outlet_id.in_(allowed_outlet_ids) | model.outlet_id.is_(None))
    return query.filter(model.outlet_id.in_(allowed_outlet_ids))
