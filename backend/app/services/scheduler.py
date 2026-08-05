"""
Background Jobs
-----------------
Runs the alert scanner and recommendation refresh on a schedule instead of
relying on someone clicking a button. Uses APScheduler's in-process
BackgroundScheduler, which is fine for a single-instance deployment (a
student project or small production setup); for multi-instance deployments,
swap this for a proper task queue (Celery/RQ) so the job doesn't run once
per instance.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.services.alert_generator import scan_and_generate_alerts

logger = logging.getLogger("franchiseops")

scheduler = BackgroundScheduler()


def _run_alert_scan_job():
    db = SessionLocal()
    try:
        created = scan_and_generate_alerts(db)
        logger.info(f"[scheduled] Alert scan complete — {created} new alert(s).")
    except Exception:
        logger.exception("[scheduled] Alert scan failed")
    finally:
        db.close()


def start_scheduler():
    # Every 15 minutes — adjust to taste. Recommendation refresh is left as a
    # manual/admin action (POST /api/v1/recommendations/refresh) since it's
    # more disruptive (it clears open recommendations before regenerating).
    scheduler.add_job(_run_alert_scan_job, "interval", minutes=15, id="alert_scan", replace_existing=True)
    scheduler.start()
    logger.info("Background scheduler started — alert scan runs every 15 minutes.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
