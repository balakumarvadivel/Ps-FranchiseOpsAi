from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class AuditCreate(BaseModel):
    outlet_id: int
    scheduled_date: date
    auditor_name: Optional[str] = None


class AuditComplete(BaseModel):
    completed_date: date
    compliance_score: float = Field(..., ge=0, le=100)
    verification_score: Optional[float] = Field(None, ge=0, le=100)
    approval_score: Optional[float] = Field(None, ge=0, le=100)


class AuditReportCreate(BaseModel):
    audit_id: int
    category: str = Field(..., pattern="^(hygiene|financial|safety|inventory)$")
    finding: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    is_violation: bool = False
    responsible_person: Optional[str] = None
    due_date: Optional[date] = None


class AuditReportResolve(BaseModel):
    resolution: Optional[str] = None


class AuditOut(BaseModel):
    id: int
    outlet_id: int
    scheduled_date: date
    completed_date: Optional[date]
    status: str
    compliance_score: Optional[float]
    risk_score: Optional[float]
    verification_score: Optional[float] = None
    approval_score: Optional[float] = None
    approval_stage: Optional[str] = None
    auditor_name: Optional[str]

    class Config:
        from_attributes = True


class AuditReportOut(BaseModel):
    id: int
    audit_id: int
    category: Optional[str]
    finding: str
    severity: str
    is_violation: bool
    resolved: bool
    responsible_person: Optional[str] = None
    due_date: Optional[date] = None
    resolution: Optional[str] = None

    class Config:
        from_attributes = True


class AuditEvidenceCreate(BaseModel):
    audit_id: int
    evidence_type: str = Field(..., pattern="^(photo|document|receipt|checklist|log)$")
    description: Optional[str] = None
    submitted_date: date
    expiry_date: Optional[date] = None


class AuditEvidenceVerify(BaseModel):
    verification_status: str = Field(..., pattern="^(verified|rejected)$")
    verification_score: Optional[float] = Field(None, ge=0, le=100)


class AuditEvidenceOut(BaseModel):
    id: int
    audit_id: int
    evidence_type: str
    description: Optional[str]
    submitted_date: date
    verification_status: str
    verification_score: Optional[float]
    expiry_date: Optional[date]

    class Config:
        from_attributes = True


class AuditApprovalDecision(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected|changes_requested)$")
    comments: Optional[str] = None


class AuditApprovalOut(BaseModel):
    id: int
    audit_id: int
    stage: str
    approver_name: Optional[str]
    status: str
    decided_at: Optional[datetime]
    comments: Optional[str]

    class Config:
        from_attributes = True
