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


class PayrollCreate(BaseModel):
    employee_id: int
    month: date
    base_salary: float = Field(..., gt=0)
    overtime_pay: float = 0
    deductions: float = 0


class EmployeePerformance(BaseModel):
    employee_id: int
    full_name: str
    outlet_id: int
    attendance_rate: float
    shift_completion_rate: float
    performance_score: float
    attrition_risk: str  # low | medium | high
