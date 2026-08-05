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


class AuditReportCreate(BaseModel):
    audit_id: int
    category: str = Field(..., pattern="^(hygiene|financial|safety|inventory)$")
    finding: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    is_violation: bool = False


class AuditOut(BaseModel):
    id: int
    outlet_id: int
    scheduled_date: date
    completed_date: Optional[date]
    status: str
    compliance_score: Optional[float]
    risk_score: Optional[float]
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

    class Config:
        from_attributes = True
