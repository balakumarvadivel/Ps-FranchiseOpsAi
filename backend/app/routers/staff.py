from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.staff import Employee, Attendance, Shift, Payroll, LeaveRequest
from app.schemas.staff import (
    EmployeeCreate, EmployeeOut, AttendanceMark, ShiftCreate, ShiftOut,
    PayrollCreate, PayrollOut, EmployeePerformance,
    LeaveRequestCreate, LeaveRequestOut, LeaveDecision,
)
from app.services.ai.staff_ai import compute_employee_performance, best_employee, shift_optimization_suggestions

router = APIRouter(prefix="/api/v1/staff", tags=["Staff Agent"])


def _assert_outlet_access(outlet_id: int, current_user: User, db: Session):
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")


@router.get("/employees", response_model=list[EmployeeOut])
def list_employees(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(Employee)
    if allowed is not None:
        query = query.filter(Employee.outlet_id.in_(allowed))
    if outlet_id:
        _assert_outlet_access(outlet_id, current_user, db)
        query = query.filter(Employee.outlet_id == outlet_id)
    return query.order_by(Employee.full_name).all()


@router.post("/employees", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager", "outlet_manager"))])
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _assert_outlet_access(payload.outlet_id, current_user, db)
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
    _assert_outlet_access(employee.outlet_id, current_user, db)

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
    _assert_outlet_access(employee.outlet_id, current_user, db)

    shift = Shift(**payload.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return {"id": shift.id, "message": "Shift scheduled"}


@router.get("/shifts", response_model=list[ShiftOut])
def list_shifts(outlet_id: Optional[int] = None, employee_id: Optional[int] = None,
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(Shift).join(Employee, Employee.id == Shift.employee_id)
    if allowed is not None:
        query = query.filter(Employee.outlet_id.in_(allowed))
    if outlet_id:
        _assert_outlet_access(outlet_id, current_user, db)
        query = query.filter(Employee.outlet_id == outlet_id)
    if employee_id:
        query = query.filter(Shift.employee_id == employee_id)

    rows = query.order_by(Shift.shift_date.desc()).limit(200).all()
    return [
        ShiftOut(id=s.id, employee_id=s.employee_id, employee_name=s.employee.full_name,
                 shift_date=s.shift_date, start_time=s.start_time, end_time=s.end_time, status=s.status)
        for s in rows
    ]


@router.post("/payroll", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager"))])
def record_payroll(payload: PayrollCreate, db: Session = Depends(get_db)):
    net_pay = payload.base_salary + payload.overtime_pay - payload.deductions
    payroll = Payroll(**payload.model_dump(), net_pay=net_pay)
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return {"id": payroll.id, "net_pay": float(net_pay)}


@router.get("/payroll", response_model=list[PayrollOut])
def list_payroll(outlet_id: Optional[int] = None, employee_id: Optional[int] = None,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(Payroll).join(Employee, Employee.id == Payroll.employee_id)
    if allowed is not None:
        query = query.filter(Employee.outlet_id.in_(allowed))
    if outlet_id:
        _assert_outlet_access(outlet_id, current_user, db)
        query = query.filter(Employee.outlet_id == outlet_id)
    if employee_id:
        query = query.filter(Payroll.employee_id == employee_id)

    rows = query.order_by(Payroll.month.desc()).limit(200).all()
    return [
        PayrollOut(
            id=p.id, employee_id=p.employee_id, employee_name=p.employee.full_name, month=p.month,
            base_salary=float(p.base_salary), overtime_pay=float(p.overtime_pay), deductions=float(p.deductions),
            net_pay=float(p.net_pay), paid_on=p.paid_on,
        )
        for p in rows
    ]


# --- Leave management -------------------------------------------------------------
@router.post("/leave", response_model=LeaveRequestOut, status_code=status.HTTP_201_CREATED)
def request_leave(payload: LeaveRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    _assert_outlet_access(employee.outlet_id, current_user, db)

    if payload.end_date < payload.start_date:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "end_date cannot be before start_date")

    leave = LeaveRequest(**payload.model_dump())
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return LeaveRequestOut(
        id=leave.id, employee_id=leave.employee_id, employee_name=employee.full_name,
        leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date,
        reason=leave.reason, status=leave.status, requested_at=leave.requested_at,
    )


@router.get("/leave", response_model=list[LeaveRequestOut])
def list_leave_requests(outlet_id: Optional[int] = None, status_filter: Optional[str] = None,
                         db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(LeaveRequest).join(Employee, Employee.id == LeaveRequest.employee_id)
    if allowed is not None:
        query = query.filter(Employee.outlet_id.in_(allowed))
    if outlet_id:
        _assert_outlet_access(outlet_id, current_user, db)
        query = query.filter(Employee.outlet_id == outlet_id)
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)

    rows = query.order_by(LeaveRequest.requested_at.desc()).all()
    return [
        LeaveRequestOut(
            id=l.id, employee_id=l.employee_id, employee_name=l.employee.full_name, leave_type=l.leave_type,
            start_date=l.start_date, end_date=l.end_date, reason=l.reason, status=l.status, requested_at=l.requested_at,
        )
        for l in rows
    ]


@router.put("/leave/{leave_id}/decision", response_model=LeaveRequestOut,
            dependencies=[Depends(require_role("admin", "regional_manager", "outlet_manager"))])
def decide_leave_request(leave_id: int, payload: LeaveDecision, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Leave request not found")
    _assert_outlet_access(leave.employee.outlet_id, current_user, db)

    leave.status = payload.status
    leave.decided_at = datetime.utcnow()
    leave.decided_by = current_user.id
    db.commit()
    db.refresh(leave)
    return LeaveRequestOut(
        id=leave.id, employee_id=leave.employee_id, employee_name=leave.employee.full_name,
        leave_type=leave.leave_type, start_date=leave.start_date, end_date=leave.end_date,
        reason=leave.reason, status=leave.status, requested_at=leave.requested_at,
    )


@router.get("/performance", response_model=list[EmployeePerformance])
def employee_performance(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """AI feature: Employee Performance Score + Attrition Prediction, per employee."""
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(Employee).filter(Employee.status == "active")
    if allowed is not None:
        query = query.filter(Employee.outlet_id.in_(allowed))
    if outlet_id:
        _assert_outlet_access(outlet_id, current_user, db)
        query = query.filter(Employee.outlet_id == outlet_id)

    return [EmployeePerformance(**compute_employee_performance(db, e)) for e in query.all()]


@router.get("/best-employee/{outlet_id}", response_model=EmployeePerformance)
def get_best_employee(outlet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI feature: Recommend Best Employee."""
    _assert_outlet_access(outlet_id, current_user, db)
    result = best_employee(db, outlet_id)
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No active employees at this outlet")
    return EmployeePerformance(**result)


@router.get("/shift-optimization/{outlet_id}")
def get_shift_optimization(outlet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI feature: Suggest Shift Optimization."""
    _assert_outlet_access(outlet_id, current_user, db)
    return {"outlet_id": outlet_id, "suggestions": shift_optimization_suggestions(db, outlet_id)}
