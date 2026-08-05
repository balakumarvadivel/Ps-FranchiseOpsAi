from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.staff import Employee, Attendance, Shift, Payroll
from app.schemas.staff import (
    EmployeeCreate, EmployeeOut, AttendanceMark, ShiftCreate, PayrollCreate, EmployeePerformance,
)
from app.services.ai.staff_ai import compute_employee_performance, best_employee, shift_optimization_suggestions

router = APIRouter(prefix="/api/v1/staff", tags=["Staff Agent"])


def _assert_outlet_access(outlet_id: int, current_user: User):
    allowed = scoped_outlet_ids(current_user)
    if allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")


@router.get("/employees", response_model=list[EmployeeOut])
def list_employees(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Employee)
    if allowed is not None:
        query = query.filter(Employee.outlet_id.in_(allowed))
    if outlet_id:
        _assert_outlet_access(outlet_id, current_user)
        query = query.filter(Employee.outlet_id == outlet_id)
    return query.order_by(Employee.full_name).all()


@router.post("/employees", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager", "outlet_manager"))])
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _assert_outlet_access(payload.outlet_id, current_user)
    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.post("/attendance", status_code=status.HTTP_201_CREATED)
def mark_attendance(payload: AttendanceMark, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    _assert_outlet_access(employee.outlet_id, current_user)

    existing = db.query(Attendance).filter(
        Attendance.employee_id == payload.employee_id, Attendance.date == payload.date,
    ).first()
    if existing:
        existing.status = payload.status
        existing.check_in = payload.check_in
        existing.check_out = payload.check_out
    else:
        db.add(Attendance(**payload.model_dump()))
    db.commit()
    return {"message": "Attendance recorded"}


@router.post("/shifts", status_code=status.HTTP_201_CREATED)
def schedule_shift(payload: ShiftCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    _assert_outlet_access(employee.outlet_id, current_user)

    shift = Shift(**payload.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return {"id": shift.id, "message": "Shift scheduled"}


@router.post("/payroll", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager"))])
def record_payroll(payload: PayrollCreate, db: Session = Depends(get_db)):
    net_pay = payload.base_salary + payload.overtime_pay - payload.deductions
    payroll = Payroll(**payload.model_dump(), net_pay=net_pay)
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return {"id": payroll.id, "net_pay": float(net_pay)}


@router.get("/performance", response_model=list[EmployeePerformance])
def employee_performance(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """AI feature: Employee Performance Score + Attrition Prediction, per employee."""
    allowed = scoped_outlet_ids(current_user)
    query = db.query(Employee).filter(Employee.status == "active")
    if allowed is not None:
        query = query.filter(Employee.outlet_id.in_(allowed))
    if outlet_id:
        _assert_outlet_access(outlet_id, current_user)
        query = query.filter(Employee.outlet_id == outlet_id)

    return [EmployeePerformance(**compute_employee_performance(db, e)) for e in query.all()]


@router.get("/best-employee/{outlet_id}", response_model=EmployeePerformance)
def get_best_employee(outlet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI feature: Recommend Best Employee."""
    _assert_outlet_access(outlet_id, current_user)
    result = best_employee(db, outlet_id)
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No active employees at this outlet")
    return EmployeePerformance(**result)


@router.get("/shift-optimization/{outlet_id}")
def get_shift_optimization(outlet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI feature: Suggest Shift Optimization."""
    _assert_outlet_access(outlet_id, current_user)
    return {"outlet_id": outlet_id, "suggestions": shift_optimization_suggestions(db, outlet_id)}
