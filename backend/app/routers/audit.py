from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.marketing_audit import Audit, AuditReport
from app.schemas.audit import AuditCreate, AuditComplete, AuditReportCreate, AuditOut, AuditReportOut
from app.services.ai.audit_ai import compute_audit_risk, compliance_recommendation
from app.services.ai.anomaly import iqr_anomalies

router = APIRouter(prefix="/api/v1/audits", tags=["Audit Agent"])


@router.get("", response_model=list[AuditOut])
def list_audits(outlet_id: Optional[int] = None, status_filter: Optional[str] = None,
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Audit)
    if allowed is not None:
        query = query.filter(Audit.outlet_id.in_(allowed))
    if outlet_id:
        query = query.filter(Audit.outlet_id == outlet_id)
    if status_filter:
        query = query.filter(Audit.status == status_filter)
    return query.order_by(Audit.scheduled_date.desc()).all()


@router.get("/pending", response_model=list[AuditOut])
def pending_audits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Audit).filter(Audit.status != "completed")
    if allowed is not None:
        query = query.filter(Audit.outlet_id.in_(allowed))
    return query.order_by(Audit.scheduled_date).all()


@router.post("", response_model=AuditOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager"))])
def schedule_audit(payload: AuditCreate, db: Session = Depends(get_db)):
    audit = Audit(**payload.model_dump(), status="pending")
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


@router.put("/{audit_id}/complete", response_model=AuditOut,
            dependencies=[Depends(require_role("admin", "regional_manager"))])
def complete_audit(audit_id: int, payload: AuditComplete, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    audit.completed_date = payload.completed_date
    audit.compliance_score = payload.compliance_score
    audit.status = "completed"
    db.commit()
    db.refresh(audit)

    # Recompute and store the risk score now that compliance_score is known.
    risk_data = compute_audit_risk(db, audit)
    audit.risk_score = risk_data["risk_score"]
    db.commit()
    db.refresh(audit)
    return audit


@router.post("/reports", response_model=AuditReportOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager"))])
def add_audit_finding(payload: AuditReportCreate, db: Session = Depends(get_db)):
    if not db.query(Audit).filter(Audit.id == payload.audit_id).first():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    report = AuditReport(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/{audit_id}/reports", response_model=list[AuditReportOut])
def get_audit_reports(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(AuditReport).filter(AuditReport.audit_id == audit_id).all()


@router.put("/reports/{report_id}/resolve", response_model=AuditReportOut,
            dependencies=[Depends(require_role("admin", "regional_manager", "outlet_manager"))])
def resolve_audit_finding(report_id: int, db: Session = Depends(get_db)):
    report = db.query(AuditReport).filter(AuditReport.id == report_id).first()
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Finding not found")
    report.resolved = True
    db.commit()
    db.refresh(report)
    return report


@router.get("/{audit_id}/risk")
def get_audit_risk(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI feature: Risk Detection, Fraud Detection, Risk Score."""
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    risk_data = compute_audit_risk(db, audit)
    risk_data["recommendation"] = compliance_recommendation(risk_data)
    return risk_data


@router.get("/risk/overview")
def risk_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Network-wide risk dashboard: every completed audit's risk score, sorted highest-risk first."""
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Audit).filter(Audit.status == "completed")
    if allowed is not None:
        query = query.filter(Audit.outlet_id.in_(allowed))

    results = []
    for audit in query.all():
        risk_data = compute_audit_risk(db, audit)
        risk_data["recommendation"] = compliance_recommendation(risk_data)
        results.append(risk_data)

    return sorted(results, key=lambda r: r["risk_score"], reverse=True)


@router.get("/compliance/trend")
def compliance_trend(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Compliance score over time — powers the Audit Score Trend chart."""
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Audit).filter(Audit.status == "completed", Audit.completed_date.isnot(None))
    if allowed is not None:
        query = query.filter(Audit.outlet_id.in_(allowed))

    audits = sorted(query.all(), key=lambda a: a.completed_date)
    return [
        {"date": a.completed_date.strftime("%Y-%m-%d"), "outlet_id": a.outlet_id, "compliance_score": float(a.compliance_score or 0)}
        for a in audits
    ]


@router.get("/compliance/anomalies")
def compliance_anomalies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    AI feature: Anomaly Detection (IQR method) across all completed audits'
    compliance scores — flags outlets whose score is unusually far from the
    network's typical range, which is a different (more robust to a few bad
    outliers) signal than the risk score alone.
    """
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Audit).filter(Audit.status == "completed", Audit.compliance_score.isnot(None))
    if allowed is not None:
        query = query.filter(Audit.outlet_id.in_(allowed))

    audits = query.all()
    if len(audits) < 4:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not enough completed audits to detect anomalies (need 4+)")

    scores = [float(a.compliance_score) for a in audits]
    flags = iqr_anomalies(scores)

    return [
        {"audit_id": audits[i].id, "outlet_id": audits[i].outlet_id, "compliance_score": scores[i]}
        for i in range(len(audits)) if flags[i]
    ]
