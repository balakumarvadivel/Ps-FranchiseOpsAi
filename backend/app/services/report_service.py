"""
Reports module
---------------
`build_report_rows` assembles the dataset for a given report_type as a list
of flat dicts (easy to hand to pandas/csv/reportlab). `write_report_file`
then serializes that dataset to PDF, Excel, or CSV under `generated_reports/`.
"""
import os
from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import Outlet
from app.models.sales import Sale
from app.models.inventory import Inventory
from app.models.staff import Employee
from app.models.marketing_audit import MarketingCampaign, Audit
from app.services.ai.health_score import compute_outlet_health_score
from app.services.ai.staff_ai import compute_employee_performance

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def build_report_rows(db: Session, report_type: str, outlet_id: Optional[int],
                       date_from: Optional[date], date_to: Optional[date]) -> tuple[str, list[dict]]:
    if report_type == "sales":
        query = db.query(Sale)
        if outlet_id:
            query = query.filter(Sale.outlet_id == outlet_id)
        if date_from:
            query = query.filter(Sale.sale_date >= date_from)
        if date_to:
            query = query.filter(Sale.sale_date <= date_to)
        rows = [{
            "Outlet": s.outlet.name, "Product": s.product.name, "Quantity": s.quantity,
            "Unit Price": float(s.unit_price), "Discount": float(s.discount),
            "Total": float(s.total_amount), "Date": s.sale_date.strftime("%Y-%m-%d %H:%M"),
        } for s in query.order_by(Sale.sale_date.desc()).limit(5000).all()]
        return "Sales Report", rows

    if report_type == "inventory":
        query = db.query(Inventory)
        if outlet_id:
            query = query.filter(Inventory.outlet_id == outlet_id)
        rows = [{
            "Outlet": i.outlet.name, "Product": i.product.name, "Quantity": i.quantity,
            "Status": i.warehouse_status, "Reorder Level": i.product.reorder_level,
        } for i in query.all()]
        return "Inventory Report", rows

    if report_type == "staff":
        query = db.query(Employee).filter(Employee.status == "active")
        if outlet_id:
            query = query.filter(Employee.outlet_id == outlet_id)
        rows = []
        for e in query.all():
            perf = compute_employee_performance(db, e)
            rows.append({
                "Employee": e.full_name, "Outlet": e.outlet.name, "Designation": e.designation,
                "Attendance %": perf["attendance_rate"], "Performance Score": perf["performance_score"],
                "Attrition Risk": perf["attrition_risk"],
            })
        return "Staff Performance Report", rows

    if report_type == "marketing":
        query = db.query(MarketingCampaign)
        if outlet_id:
            query = query.filter(MarketingCampaign.outlet_id == outlet_id)
        rows = [{
            "Campaign": c.name, "Channel": c.channel, "Budget": float(c.budget),
            "Ad Cost": float(c.ad_cost), "Revenue Generated": float(c.revenue_generated),
            "ROI %": c.roi_percent, "Status": c.status,
        } for c in query.all()]
        return "Marketing Report", rows

    if report_type == "audit":
        query = db.query(Audit)
        if outlet_id:
            query = query.filter(Audit.outlet_id == outlet_id)
        rows = [{
            "Outlet": a.outlet.name, "Scheduled": a.scheduled_date, "Completed": a.completed_date,
            "Status": a.status, "Compliance Score": a.compliance_score, "Risk Score": a.risk_score,
        } for a in query.all()]
        return "Audit Report", rows

    # overall — cross-domain outlet summary
    outlets = db.query(Outlet)
    if outlet_id:
        outlets = outlets.filter(Outlet.id == outlet_id)
    rows = []
    for o in outlets.all():
        revenue = sum(float(s.total_amount) for s in
                      db.query(Sale).filter(Sale.outlet_id == o.id).all())
        rows.append({
            "Outlet": o.name, "City": o.city, "Region": o.region,
            "Total Revenue": round(revenue, 2), "Health Score": compute_outlet_health_score(db, o.id),
            "Status": o.status,
        })
    return "Overall Business Report", rows


def write_report_file(title: str, rows: list[dict], fmt: str, filename_base: str) -> str:
    if not rows:
        rows = [{"message": "No data available for the selected filters"}]

    if fmt == "csv":
        import csv
        path = os.path.join(REPORTS_DIR, f"{filename_base}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path

    if fmt == "excel":
        import pandas as pd
        path = os.path.join(REPORTS_DIR, f"{filename_base}.xlsx")
        pd.DataFrame(rows).to_excel(path, index=False, sheet_name=title[:31])
        return path

    if fmt == "pdf":
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        path = os.path.join(REPORTS_DIR, f"{filename_base}.pdf")
        doc = SimpleDocTemplate(path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()

        headers = list(rows[0].keys())
        data = [headers] + [[str(row.get(h, "")) for h in headers] for row in rows[:500]]

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ]))

        elements = [
            Paragraph(title, styles["Title"]),
            Paragraph(f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} — FranchiseOps AI", styles["Normal"]),
            Spacer(1, 12),
            table,
        ]
        doc.build(elements)
        return path

    raise ValueError(f"Unsupported format: {fmt}")
