"""
Alerts Center — generation logic
---------------------------------
`scan_and_generate_alerts` inspects the current state of the database and
creates Alert rows for anything that needs attention right now. It's
idempotent-ish: it skips creating a duplicate alert of the same type for the
same outlet if an unread one from the last 24 hours already exists, so
re-running the scan (e.g. on a schedule) doesn't spam the alerts feed.
"""
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.user import Outlet
from app.models.inventory import Inventory, InventoryBatch
from app.models.staff import Employee, Attendance
from app.models.marketing_audit import Audit, MarketingCampaign
from app.models.ai import Alert
from app.services.ai.health_score import compute_outlet_health_score


def _already_alerted_recently(db: Session, outlet_id, alert_type: str) -> bool:
    since = datetime.utcnow() - timedelta(hours=24)
    return db.query(Alert).filter(
        Alert.outlet_id == outlet_id, Alert.type == alert_type, Alert.created_at >= since,
    ).first() is not None


def _create(db: Session, outlet_id, alert_type: str, message: str, severity: str):
    if _already_alerted_recently(db, outlet_id, alert_type):
        return
    db.add(Alert(outlet_id=outlet_id, type=alert_type, message=message, severity=severity))


def scan_and_generate_alerts(db: Session) -> int:
    count_before = db.query(Alert).count()

    today = date.today()

    # --- Low stock / out of stock -------------------------------------
    low_stock_rows = db.query(Inventory).filter(Inventory.warehouse_status.in_(["low_stock", "out_of_stock"])).all()
    for row in low_stock_rows:
        severity = "critical" if row.warehouse_status == "out_of_stock" else "high"
        _create(db, row.outlet_id, "low_stock",
                f"{row.product.name} is {row.warehouse_status.replace('_', ' ')} at {row.outlet.name} "
                f"({row.quantity} units left).", severity)

    # --- Expiring / expired products ----------------------------------
    soon = today + timedelta(days=7)
    batches = db.query(InventoryBatch).filter(InventoryBatch.expiry_date.isnot(None),
                                               InventoryBatch.expiry_date <= soon).all()
    for batch in batches:
        inv = batch.inventory
        if batch.expiry_date < today:
            _create(db, inv.outlet_id, "expired",
                    f"Batch {batch.batch_number} of {inv.product.name} expired on {batch.expiry_date}.", "critical")
        else:
            _create(db, inv.outlet_id, "expiring_soon",
                    f"Batch {batch.batch_number} of {inv.product.name} expires on {batch.expiry_date}.", "high")

    # --- Poor outlet performance (health score) ------------------------
    for outlet in db.query(Outlet).all():
        health = compute_outlet_health_score(db, outlet.id)
        if health < 50:
            _create(db, outlet.id, "poor_performance",
                    f"{outlet.name} health score has dropped to {health}/100.", "critical" if health < 35 else "high")

    # --- Staff shortage (attendance rate) ------------------------------
    since_7 = today - timedelta(days=7)
    for outlet in db.query(Outlet).all():
        employee_ids = [e.id for e in db.query(Employee.id).filter(Employee.outlet_id == outlet.id).all()]
        if not employee_ids:
            continue
        total = db.query(Attendance).filter(Attendance.employee_id.in_(employee_ids), Attendance.date >= since_7).count()
        if not total:
            continue
        present = db.query(Attendance).filter(
            Attendance.employee_id.in_(employee_ids), Attendance.date >= since_7, Attendance.status == "present",
        ).count()
        rate = present / total
        if rate < 0.75:
            _create(db, outlet.id, "staff_shortage",
                    f"{outlet.name} attendance rate over the last 7 days is {round(rate * 100)}%.", "high")

    # --- Audit due -------------------------------------------------------
    overdue_audits = db.query(Audit).filter(Audit.status != "completed", Audit.scheduled_date < today).all()
    for audit in overdue_audits:
        days_overdue = (today - audit.scheduled_date).days
        _create(db, audit.outlet_id, "audit_due",
                f"Audit for outlet #{audit.outlet_id} is {days_overdue} days overdue.",
                "critical" if days_overdue > 30 else "medium")

    # --- Marketing campaign ending soon ---------------------------------
    ending_soon = today + timedelta(days=3)
    campaigns = db.query(MarketingCampaign).filter(
        MarketingCampaign.status == "active", MarketingCampaign.end_date.isnot(None),
        MarketingCampaign.end_date <= ending_soon,
    ).all()
    for c in campaigns:
        _create(db, c.outlet_id, "campaign_ending",
                f"Campaign '{c.name}' ends on {c.end_date}.", "low")

    db.commit()
    return db.query(Alert).count() - count_before
