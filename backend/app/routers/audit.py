from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.core.pagination import Pagination, paginate_with_headers
from app.database import get_db
from app.models.user import User
from app.models.marketing_audit import Audit, AuditReport, AuditEvidence, AuditApproval
from app.schemas.audit import (
    AuditCreate, AuditComplete, AuditReportCreate, AuditReportResolve, AuditOut, AuditReportOut,
    AuditEvidenceCreate, AuditEvidenceVerify, AuditEvidenceOut, AuditApprovalDecision, AuditApprovalOut,
)
from app.services.ai.audit_ai import compute_audit_risk, compliance_recommendation
from app.services.ai.anomaly import iqr_anomalies

router = APIRouter(prefix="/api/v1/audits", tags=["Audit Agent"])

APPROVAL_STAGES = ["auditor_review", "supervisor_review", "manager_approval", "final_approval"]


@router.get("", response_model=list[AuditOut])
def list_audits(response: Response, outlet_id: Optional[int] = None, status_filter: Optional[str] = None,
                 pagination: Pagination = Depends(),
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(Audit)
    if allowed is not None:
        query = query.filter(Audit.outlet_id.in_(allowed))
    if outlet_id:
        query = query.filter(Audit.outlet_id == outlet_id)
    if status_filter:
        query = query.filter(Audit.status == status_filter)
    return paginate_with_headers(query.order_by(Audit.scheduled_date.desc()), pagination, response)


@router.get("/pending", response_model=list[AuditOut])
def pending_audits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(Audit).filter(Audit.status != "completed")
    if allowed is not None:
        query = query.filter(Audit.outlet_id.in_(allowed))
    return query.order_by(Audit.scheduled_date).all()


@router.post("", response_model=AuditOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager"))])
def schedule_audit(payload: AuditCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and payload.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")
    audit = Audit(**payload.model_dump(), status="pending")
    db.add(audit)
    db.commit()
    db.refresh(audit)

    # Every audit gets the same 4-stage approval workflow, seeded as pending.
    for stage in APPROVAL_STAGES:
        db.add(AuditApproval(audit_id=audit.id, stage=stage, status="pending"))
    db.commit()

    return audit


@router.put("/{audit_id}/complete", response_model=AuditOut,
            dependencies=[Depends(require_role("admin", "regional_manager"))])
def complete_audit(audit_id: int, payload: AuditComplete, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    audit.completed_date = payload.completed_date
    audit.compliance_score = payload.compliance_score
    audit.verification_score = payload.verification_score
    audit.approval_score = payload.approval_score
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
def add_audit_finding(payload: AuditReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(Audit).filter(Audit.id == payload.audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")
    report = AuditReport(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/{audit_id}/reports", response_model=list[AuditReportOut])
def get_audit_reports(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")
    return db.query(AuditReport).filter(AuditReport.audit_id == audit_id).all()


@router.put("/reports/{report_id}/resolve", response_model=AuditReportOut,
            dependencies=[Depends(require_role("admin", "regional_manager", "outlet_manager"))])
def resolve_audit_finding(report_id: int, payload: AuditReportResolve = AuditReportResolve(),
                           db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(AuditReport).filter(AuditReport.id == report_id).first()
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Finding not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and report.audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")
    report.resolved = True
    if payload.resolution:
        report.resolution = payload.resolution
    db.commit()
    db.refresh(report)
    return report


@router.get("/{audit_id}/risk")
def get_audit_risk(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI feature: Risk Detection, Fraud Detection, Risk Score."""
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")
    risk_data = compute_audit_risk(db, audit)
    risk_data["recommendation"] = compliance_recommendation(risk_data)
    return risk_data


@router.get("/risk/overview")
def risk_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Network-wide risk dashboard: every completed audit's risk score, sorted highest-risk first."""
    allowed = scoped_outlet_ids(current_user, db)
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
    allowed = scoped_outlet_ids(current_user, db)
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
    allowed = scoped_outlet_ids(current_user, db)
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


# --- Evidence -------------------------------------------------------------
@router.post("/evidence", response_model=AuditEvidenceOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager", "outlet_manager"))])
def submit_evidence(payload: AuditEvidenceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(Audit).filter(Audit.id == payload.audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")
    evidence = AuditEvidence(**payload.model_dump())
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/{audit_id}/evidence", response_model=list[AuditEvidenceOut])
def list_evidence(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")
    return db.query(AuditEvidence).filter(AuditEvidence.audit_id == audit_id).all()


@router.put("/evidence/{evidence_id}/verify", response_model=AuditEvidenceOut,
            dependencies=[Depends(require_role("admin", "regional_manager"))])
def verify_evidence(evidence_id: int, payload: AuditEvidenceVerify, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    evidence = db.query(AuditEvidence).filter(AuditEvidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evidence not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and evidence.audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")
    evidence.verification_status = payload.verification_status
    evidence.verification_score = payload.verification_score
    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/evidence/expiring")
def expiring_evidence(within_days: int = 30, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Evidence with an expiry_date (licenses, certificates) expiring soon or already expired."""
    from datetime import timedelta
    allowed = scoped_outlet_ids(current_user, db)
    cutoff = date.today() + timedelta(days=within_days)
    query = db.query(AuditEvidence).join(Audit, Audit.id == AuditEvidence.audit_id).filter(
        AuditEvidence.expiry_date.isnot(None), AuditEvidence.expiry_date <= cutoff,
    )
    if allowed is not None:
        query = query.filter(Audit.outlet_id.in_(allowed))
    rows = query.all()
    return [
        {
            "id": e.id, "audit_id": e.audit_id, "outlet_id": e.audit.outlet_id,
            "evidence_type": e.evidence_type, "description": e.description,
            "expiry_date": e.expiry_date.isoformat(), "is_expired": e.expiry_date < date.today(),
        }
        for e in rows
    ]


# --- Approval workflow -------------------------------------------------------------
@router.get("/{audit_id}/approvals", response_model=list[AuditApprovalOut])
def list_approvals(audit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")
    rows = db.query(AuditApproval).filter(AuditApproval.audit_id == audit_id).all()
    stage_order = {s: i for i, s in enumerate(APPROVAL_STAGES)}
    return sorted(rows, key=lambda a: stage_order.get(a.stage, 99))


@router.put("/approvals/{approval_id}/decision", response_model=AuditApprovalOut,
            dependencies=[Depends(require_role("admin", "regional_manager"))])
def decide_approval(approval_id: int, payload: AuditApprovalDecision, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """
    Approve/reject/request-changes on one stage of the audit's 4-stage
    workflow (auditor_review -> supervisor_review -> manager_approval ->
    final_approval). Approving the last stage marks the audit's overall
    approval_stage as 'approved'; a rejection or changes-requested at any
    stage short-circuits the whole workflow to that outcome.
    """
    approval = db.query(AuditApproval).filter(AuditApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Approval step not found")

    audit = db.query(Audit).filter(Audit.id == approval.audit_id).first()
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and audit.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet's audits")

    approval.status = payload.status
    approval.approver_name = current_user.full_name
    approval.decided_at = datetime.utcnow()
    approval.comments = payload.comments
    db.commit()
    db.refresh(approval)

    if payload.status in ("rejected", "changes_requested"):
        audit.approval_stage = payload.status
    elif payload.status == "approved":
        stage_index = APPROVAL_STAGES.index(approval.stage) if approval.stage in APPROVAL_STAGES else -1
        if stage_index == len(APPROVAL_STAGES) - 1:
            audit.approval_stage = "approved"
        elif stage_index >= 0:
            audit.approval_stage = APPROVAL_STAGES[stage_index + 1]
    db.commit()

    return approval
