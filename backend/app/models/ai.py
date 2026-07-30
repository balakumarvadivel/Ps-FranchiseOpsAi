from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True)  # NULL = network-wide
    category = Column(String(50), nullable=False)  # sales|inventory|staff|marketing|audit|intelligence
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    confidence = Column(Numeric(5, 2), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), nullable=False)  # critical|high|medium|low
    category = Column(String(50), nullable=True)  # inventory|marketing|staff|audit|finance
    status = Column(String(20), default="open")  # open|in_progress|resolved|dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True)
    type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="medium")  # critical|high|medium|low
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    report_type = Column(String(50), nullable=False)  # sales|inventory|staff|marketing|audit|overall
    format = Column(String(10), nullable=False)  # pdf|excel|csv
    file_path = Column(Text, nullable=True)
    date_from = Column(Date, nullable=True)
    date_to = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SettingsModel(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String(10), default="light")  # light|dark
    notifications_enabled = Column(Boolean, default=True)
    email_alerts = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
