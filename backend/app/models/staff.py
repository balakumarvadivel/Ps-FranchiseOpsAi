from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Date, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    full_name = Column(String(150), nullable=False)
    designation = Column(String(100))
    date_joined = Column(Date)
    status = Column(String(20), default="active")  # active|on_leave|resigned
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet", back_populates="employees")
    shifts = relationship("Shift", back_populates="employee", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    payroll_records = relationship("Payroll", back_populates="employee", cascade="all, delete-orphan")


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    shift_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), default="scheduled")  # scheduled|completed|missed

    employee = relationship("Employee", back_populates="shifts")


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("employee_id", "date"),)

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="present")  # present|absent|half_day|leave

    employee = relationship("Employee", back_populates="attendance_records")


class Payroll(Base):
    __tablename__ = "payroll"
    __table_args__ = (UniqueConstraint("employee_id", "month"),)

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    month = Column(Date, nullable=False)
    base_salary = Column(Numeric(12, 2), nullable=False)
    overtime_pay = Column(Numeric(12, 2), default=0)
    deductions = Column(Numeric(12, 2), default=0)
    net_pay = Column(Numeric(12, 2), nullable=False)
    paid_on = Column(Date, nullable=True)

    employee = relationship("Employee", back_populates="payroll_records")
