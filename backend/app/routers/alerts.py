from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.core.pagination import Pagination, paginate_with_headers
from app.database import get_db
from app.models.user import User
from app.models.ai import Notification, Alert
from app.schemas.notifications import NotificationOut, AlertOut
from app.services.alert_generator import scan_and_generate_alerts

router = APIRouter(prefix="/api/v1", tags=["Notifications & Alerts"])


# --- Notifications (per logged-in user) -----------------------------------
@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(response: Response, unread_only: bool = False, pagination: Pagination = Depends(),
                        db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return paginate_with_headers(query.order_by(Notification.created_at.desc()), pagination, response)


@router.put("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    notif = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.put("/notifications/read-all")
def mark_all_notifications_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read.is_(False)) \
        .update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


# --- Alerts Center (organization-wide, scoped by role) ----------------------
@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(response: Response, severity: Optional[str] = None, alert_type: Optional[str] = None,
                 unread_only: bool = False, pagination: Pagination = Depends(),
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(Alert)
    if allowed is not None:
        query = query.filter(Alert.outlet_id.in_(allowed))
    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_type:
        query = query.filter(Alert.type == alert_type)
    if unread_only:
        query = query.filter(Alert.is_read.is_(False))
    return paginate_with_headers(query.order_by(Alert.created_at.desc()), pagination, response)


@router.put("/alerts/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and alert.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this alert")
    alert.is_read = True
    db.commit()
    return {"message": "Alert marked as read"}


@router.post("/alerts/scan", dependencies=[Depends(require_role("admin", "regional_manager"))])
def run_alert_scan(db: Session = Depends(get_db)):
    """
    Scans current inventory, audits, staff attendance, outlet health and
    campaigns, and creates new Alert rows for anything that needs attention.
    In production, call this from a scheduled job (e.g. every 15 minutes)
    instead of relying on a manual trigger.
    """
    created = scan_and_generate_alerts(db)
    return {"message": f"Alert scan complete — {created} new alert(s) created."}
