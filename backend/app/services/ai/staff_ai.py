"""
Staff Agent — AI Layer
----------------------
All rule-based / statistical, consistent with the rest of the AI layer:

  performance_score   = 0.6 * attendance_rate + 0.4 * shift_completion_rate
  attrition_risk       = rule engine on attendance TREND (last 30d vs prior 30d)
                         + absolute attendance level
  shift optimization  = compares hour-of-day sales volume against hour-of-day
                         shift coverage to flag under-staffed peak hours
"""
from collections import Counter
from datetime import date, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.staff import Employee, Attendance, Shift
from app.models.sales import Sale


def _attendance_rate(db: Session, employee_id: int, start: date, end: date) -> float:
    total = db.query(func.count(Attendance.id)).filter(
        Attendance.employee_id == employee_id, Attendance.date >= start, Attendance.date < end,
    ).scalar()
    if not total:
        return 60.0  # neutral default, no data yet
    present = db.query(func.count(Attendance.id)).filter(
        Attendance.employee_id == employee_id, Attendance.date >= start, Attendance.date < end,
        Attendance.status == "present",
    ).scalar()
    return round((present / total) * 100, 1)


def _shift_completion_rate(db: Session, employee_id: int, since: date) -> float:
    total = db.query(func.count(Shift.id)).filter(Shift.employee_id == employee_id, Shift.shift_date >= since).scalar()
    if not total:
        return 70.0  # neutral default
    completed = db.query(func.count(Shift.id)).filter(
        Shift.employee_id == employee_id, Shift.shift_date >= since, Shift.status == "completed",
    ).scalar()
    return round((completed / total) * 100, 1)


def compute_employee_performance(db: Session, employee: Employee) -> dict:
    today = date.today()
    since_30 = today - timedelta(days=30)

    attendance_rate = _attendance_rate(db, employee.id, since_30, today)
    shift_rate = _shift_completion_rate(db, employee.id, since_30)
    score = round(0.6 * attendance_rate + 0.4 * shift_rate, 1)

    # Attrition risk: compare this 30d window's attendance to the previous 30d window
    prev_start = since_30 - timedelta(days=30)
    prev_rate = _attendance_rate(db, employee.id, prev_start, since_30)
    trend = attendance_rate - prev_rate

    if attendance_rate < 70 and trend < -5:
        risk = "high"
    elif attendance_rate < 80 or trend < -3:
        risk = "medium"
    else:
        risk = "low"

    return {
        "employee_id": employee.id,
        "full_name": employee.full_name,
        "outlet_id": employee.outlet_id,
        "attendance_rate": attendance_rate,
        "shift_completion_rate": shift_rate,
        "performance_score": score,
        "attrition_risk": risk,
    }


def best_employee(db: Session, outlet_id: int) -> dict | None:
    employees = db.query(Employee).filter(Employee.outlet_id == outlet_id, Employee.status == "active").all()
    if not employees:
        return None
    scored = [compute_employee_performance(db, e) for e in employees]
    return max(scored, key=lambda r: r["performance_score"])


def shift_optimization_suggestions(db: Session, outlet_id: int, lookback_days: int = 30) -> List[str]:
    """
    Compares the hour-of-day distribution of sales volume against the
    hour-of-day distribution of scheduled shifts, and flags peak sales
    hours that appear under-covered by staff.
    """
    since = date.today() - timedelta(days=lookback_days)

    sales_rows = db.query(Sale.sale_date).filter(Sale.outlet_id == outlet_id, Sale.sale_date >= since).all()
    sales_hour_counts = Counter(row.sale_date.hour for row in sales_rows)

    employee_ids = [e.id for e in db.query(Employee.id).filter(Employee.outlet_id == outlet_id).all()]
    shift_rows = db.query(Shift.start_time).filter(
        Shift.employee_id.in_(employee_ids), Shift.shift_date >= since,
    ).all() if employee_ids else []
    shift_hour_counts = Counter(row.start_time.hour for row in shift_rows)

    if not sales_hour_counts:
        return []

    total_sales = sum(sales_hour_counts.values())
    peak_hours = [h for h, c in sales_hour_counts.items() if c / total_sales > 0.08]  # busier-than-average hours

    suggestions = []
    for hour in sorted(peak_hours):
        staff_on_shift = shift_hour_counts.get(hour, 0)
        if staff_on_shift == 0:
            suggestions.append(
                f"Peak sales hour {hour:02d}:00 has no scheduled shift starts — consider adding staff coverage."
            )
        elif staff_on_shift == 1:
            suggestions.append(
                f"Peak sales hour {hour:02d}:00 is covered by only 1 shift start — consider a second staff member."
            )
    return suggestions
