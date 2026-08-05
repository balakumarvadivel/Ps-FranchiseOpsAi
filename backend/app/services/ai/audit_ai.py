"""
Audit Agent — AI Layer
----------------------
Reuses services.ai.anomaly.risk_score_from_audit for the core risk score,
and adds a simple fraud-risk flag: an audit is flagged when compliance is
low AND at least one critical/financial violation was recorded — i.e. it's
not just "messy", it looks deliberately concerning.
"""
from sqlalchemy.orm import Session

from app.models.marketing_audit import Audit, AuditReport
from app.services.ai.anomaly import risk_score_from_audit


def compute_audit_risk(db: Session, audit: Audit) -> dict:
    reports = db.query(AuditReport).filter(AuditReport.audit_id == audit.id).all()
    violation_count = sum(1 for r in reports if r.is_violation)
    critical_count = sum(1 for r in reports if r.is_violation and r.severity == "critical")

    compliance = float(audit.compliance_score) if audit.compliance_score is not None else 70.0
    risk = risk_score_from_audit(compliance, violation_count, critical_count)

    financial_critical = any(
        r.is_violation and r.category == "financial" and r.severity in ("high", "critical") for r in reports
    )
    fraud_flag = compliance < 65 and (critical_count > 0 or financial_critical)

    return {
        "audit_id": audit.id,
        "outlet_id": audit.outlet_id,
        "compliance_score": compliance,
        "violation_count": violation_count,
        "critical_violation_count": critical_count,
        "risk_score": risk,
        "fraud_risk_flag": fraud_flag,
    }


def compliance_recommendation(risk_data: dict) -> str:
    if risk_data["fraud_risk_flag"]:
        return "Escalate to internal audit team immediately — financial irregularity pattern detected."
    if risk_data["risk_score"] >= 60:
        return "Schedule a follow-up audit within 2 weeks and require a corrective action plan."
    if risk_data["risk_score"] >= 35:
        return "Monitor at next scheduled audit cycle; no immediate escalation needed."
    return "No action needed — outlet is within acceptable compliance range."
