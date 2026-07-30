"""
Outlet Health Score
--------------------
A transparent, explainable composite score (0-100) built from five weighted
sub-metrics. Weights are documented here so they can be cited directly in a
project report/viva rather than treated as a black box.

    Sales performance   25%   -> revenue growth, last 30d vs previous 30d
    Inventory health    20%   -> % of SKUs not low/out of stock
    Staff attendance    15%   -> attendance rate, last 30 days
    Audit compliance    20%   -> average compliance_score of completed audits
    Profit margin       20%   -> average (price - cost) / price on recent sales

Any sub-metric with no underlying data defaults to a neutral 60/100 rather
than 0, so a brand-new outlet with no audit/attendance history yet isn't
unfairly penalized.
"""
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.sales import Sale
from app.models.inventory import Inventory, Product
from app.models.staff import Employee, Attendance
from app.models.marketing_audit import Audit

NEUTRAL_DEFAULT = 60.0

WEIGHTS = {
    "sales": 0.25,
    "inventory": 0.20,
    "staff": 0.15,
    "audit": 0.20,
    "profit": 0.20,
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _sales_score(db: Session, outlet_id: int) -> float:
    today = date.today()
    window_start = today - timedelta(days=30)
    prev_start = window_start - timedelta(days=30)

    current = db.query(func.coalesce(func.sum(Sale.total_amount), 0)) \
        .filter(Sale.outlet_id == outlet_id, Sale.sale_date >= window_start, Sale.sale_date < today).scalar()
    previous = db.query(func.coalesce(func.sum(Sale.total_amount), 0)) \
        .filter(Sale.outlet_id == outlet_id, Sale.sale_date >= prev_start, Sale.sale_date < window_start).scalar()

    current, previous = float(current), float(previous)
    if previous == 0:
        return NEUTRAL_DEFAULT if current == 0 else 80.0

    growth_pct = ((current - previous) / previous) * 100
    # Map growth% to a 0-100 score: 0% growth -> 60, +25% -> 100, -25% -> 20
    return _clamp(60 + growth_pct * 1.6)


def _inventory_score(db: Session, outlet_id: int) -> float:
    total = db.query(func.count(Inventory.id)).filter(Inventory.outlet_id == outlet_id).scalar()
    if not total:
        return NEUTRAL_DEFAULT
    healthy = db.query(func.count(Inventory.id)).filter(
        Inventory.outlet_id == outlet_id,
        Inventory.warehouse_status == "in_stock",
    ).scalar()
    return _clamp((healthy / total) * 100)


def _staff_score(db: Session, outlet_id: int) -> float:
    employee_ids = [e.id for e in db.query(Employee.id).filter(Employee.outlet_id == outlet_id).all()]
    if not employee_ids:
        return NEUTRAL_DEFAULT

    since = date.today() - timedelta(days=30)
    total = db.query(func.count(Attendance.id)).filter(
        Attendance.employee_id.in_(employee_ids), Attendance.date >= since,
    ).scalar()
    if not total:
        return NEUTRAL_DEFAULT
    present = db.query(func.count(Attendance.id)).filter(
        Attendance.employee_id.in_(employee_ids), Attendance.date >= since,
        Attendance.status == "present",
    ).scalar()
    return _clamp((present / total) * 100)


def _audit_score(db: Session, outlet_id: int) -> float:
    avg_score = db.query(func.avg(Audit.compliance_score)).filter(
        Audit.outlet_id == outlet_id, Audit.status == "completed",
    ).scalar()
    return float(avg_score) if avg_score is not None else NEUTRAL_DEFAULT


def _profit_score(db: Session, outlet_id: int) -> float:
    since = date.today() - timedelta(days=30)
    rows = (
        db.query(Sale.unit_price, Product.cost_price)
        .join(Product, Product.id == Sale.product_id)
        .filter(Sale.outlet_id == outlet_id, Sale.sale_date >= since)
        .all()
    )
    if not rows:
        return NEUTRAL_DEFAULT

    margins = [
        (float(price) - float(cost)) / float(price)
        for price, cost in rows if price and float(price) > 0
    ]
    if not margins:
        return NEUTRAL_DEFAULT

    avg_margin_pct = (sum(margins) / len(margins)) * 100
    # 0% margin -> 0, 50%+ margin -> 100
    return _clamp(avg_margin_pct * 2)


def compute_outlet_health_score(db: Session, outlet_id: int) -> float:
    scores = {
        "sales": _sales_score(db, outlet_id),
        "inventory": _inventory_score(db, outlet_id),
        "staff": _staff_score(db, outlet_id),
        "audit": _audit_score(db, outlet_id),
        "profit": _profit_score(db, outlet_id),
    }
    composite = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    return round(composite, 1)


def compute_outlet_health_breakdown(db: Session, outlet_id: int) -> dict:
    """Returns the individual sub-scores too — used by the detailed health-analysis view."""
    return {
        "sales_performance": round(_sales_score(db, outlet_id), 1),
        "inventory_availability": round(_inventory_score(db, outlet_id), 1),
        "staff_productivity": round(_staff_score(db, outlet_id), 1),
        "audit_compliance": round(_audit_score(db, outlet_id), 1),
        "profit_margin": round(_profit_score(db, outlet_id), 1),
        "overall": compute_outlet_health_score(db, outlet_id),
    }
