from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    outlet_id: int
    full_name: str
    designation: Optional[str] = None
    date_joined: Optional[date] = None


class EmployeeOut(BaseModel):
    id: int
    outlet_id: int
    full_name: str
    designation: Optional[str]
    date_joined: Optional[date]
    status: str

    class Config:
        from_attributes = True


class AttendanceMark(BaseModel):
    employee_id: int
    date: date
    status: str = Field(..., pattern="^(present|absent|half_day|leave)$")
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None


class ShiftCreate(BaseModel):
    employee_id: int
    shift_date: date
    start_time: time
    end_time: time


class ShiftOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    shift_date: date
    start_time: time
    end_time: time
    status: str

    class Config:
        from_attributes = True


class PayrollCreate(BaseModel):
    employee_id: int
    month: date
    base_salary: float = Field(..., gt=0)
    overtime_pay: float = 0
    deductions: float = 0


class PayrollOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    month: date
    base_salary: float
    overtime_pay: float
    deductions: float
    net_pay: float
    paid_on: Optional[date]

    class Config:
        from_attributes = True


class LeaveRequestCreate(BaseModel):
    employee_id: int
    leave_type: str = Field("casual", pattern="^(casual|sick|earned|unpaid)$")
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveRequestOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str
    requested_at: datetime

    class Config:
        from_attributes = True


class LeaveDecision(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")


class EmployeePerformance(BaseModel):
    employee_id: int
    full_name: str
    outlet_id: int
    attendance_rate: float
    shift_completion_rate: float
    performance_score: float
    attrition_risk: str  # low | medium | high
