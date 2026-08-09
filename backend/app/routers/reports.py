import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.ai import Report
from app.schemas.reports import ReportRequest, ReportOut
from app.services.report_service import build_report_rows, write_report_file

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.post("/generate", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def generate_report(payload: ReportRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    if payload.outlet_id and allowed is not None and payload.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    title, rows = build_report_rows(db, payload.report_type, payload.outlet_id, payload.date_from, payload.date_to,
                                     allowed_outlet_ids=allowed)

    filename_base = f"{payload.report_type}_{uuid.uuid4().hex[:8]}"
    file_path = write_report_file(title, rows, payload.format, filename_base)

    report = Report(
        generated_by=current_user.id, report_type=payload.report_type, format=payload.format,
        file_path=file_path, date_from=payload.date_from, date_to=payload.date_to,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=list[ReportOut])
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Report).filter(Report.generated_by == current_user.id).order_by(Report.created_at.desc()).all()


@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id, Report.generated_by == current_user.id).first()
    if not report or not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report file not found")

    media_types = {
        "pdf": "application/pdf",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
    }
    return FileResponse(
        report.file_path,
        media_type=media_types.get(report.format, "application/octet-stream"),
        filename=os.path.basename(report.file_path),
    )
