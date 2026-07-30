from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True)  # NULL = network-wide
    name = Column(String(150), nullable=False)
    channel = Column(String(50))  # social|print|in-store|email
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    budget = Column(Numeric(12, 2), nullable=False)
    ad_cost = Column(Numeric(12, 2), default=0)
    revenue_generated = Column(Numeric(14, 2), default=0)
    customer_reach = Column(Integer, default=0)
    coupon_code = Column(String(30), nullable=True)
    coupon_redemptions = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active|completed|paused
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet")

    @property
    def roi_percent(self) -> float:
        cost = float(self.ad_cost or 0)
        if cost == 0:
            return 0.0
        return round(((float(self.revenue_generated or 0) - cost) / cost) * 100, 2)


class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    status = Column(String(20), default="pending")  # pending|completed|overdue
    compliance_score = Column(Numeric(5, 2), nullable=True)
    risk_score = Column(Numeric(5, 2), nullable=True)
    auditor_name = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet")
    reports = relationship("AuditReport", back_populates="audit", cascade="all, delete-orphan")


class AuditReport(Base):
    __tablename__ = "audit_reports"

    id = Column(Integer, primary_key=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100))  # hygiene|financial|safety|inventory
    finding = Column(Text, nullable=False)
    severity = Column(String(20), default="low")  # low|medium|high|critical
    is_violation = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    audit = relationship("Audit", back_populates="reports")
