from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import require_role, get_current_user, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.sales import Sale
from app.models.inventory import Inventory
from app.models.staff import Employee
from app.schemas.data_validation import CommitRequest, CommitResult
from app.services.data_validation import read_upload, validate_dataset, SCHEMAS

router = APIRouter(prefix="/api/v1/data-validation", tags=["Data Validation & Processing"])


@router.get("/schemas")
def list_schemas():
    """Returns the required columns per dataset type, so the frontend can show an upload template."""
    return {k: {"required": v["required"]} for k, v in SCHEMAS.items()}


@router.post("/upload")
async def upload_and_validate(
    file: UploadFile = File(...),
    dataset_type: str = Form(...),
    _current_user=Depends(require_role("admin", "regional_manager", "outlet_manager")),
):
    if dataset_type not in SCHEMAS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"dataset_type must be one of {list(SCHEMAS)}")
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only .csv, .xlsx, or .xls files are supported")

    contents = await file.read()
    try:
        df = read_upload(contents, file.filename)
    except Exception as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Couldn't parse file: {exc}")

    if df.empty:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The uploaded file has no rows")

    report = validate_dataset(df, dataset_type)
    if not report["valid"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, report["error"])

    return report


@router.post("/commit", response_model=CommitResult,
             dependencies=[Depends(require_role("admin", "regional_manager"))])
def commit_cleaned_data(payload: CommitRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Inserts already-cleaned rows (as returned by /upload) into the real
    tables. Each dataset type maps to one model; rows that still fail at
    insert time (e.g. a foreign key that doesn't exist), or whose outlet_id
    falls outside the requesting user's scope (a regional_manager trying to
    import data for another region), are skipped and reported rather than
    aborting the whole batch or silently writing out-of-scope data.
    """
    if payload.dataset_type not in SCHEMAS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"dataset_type must be one of {list(SCHEMAS)}")

    allowed = scoped_outlet_ids(current_user, db)
    inserted, skipped, errors = 0, 0, []

    for i, row in enumerate(payload.rows):
        try:
            row_outlet_id = int(row["outlet_id"])
            if allowed is not None and row_outlet_id not in allowed:
                skipped += 1
                errors.append(f"Row {i}: outlet_id {row_outlet_id} is outside your authorized scope — skipped")
                continue

            if payload.dataset_type == "sales":
                quantity = int(row["quantity"])
                unit_price = float(row["unit_price"])
                db.add(Sale(
                    outlet_id=row_outlet_id, product_id=int(row["product_id"]),
                    quantity=quantity, unit_price=unit_price, total_amount=quantity * unit_price,
                    discount=float(row.get("discount") or 0),
                    sale_date=row.get("sale_date") or datetime.utcnow(),
                ))
            elif payload.dataset_type == "inventory":
                existing = db.query(Inventory).filter(
                    Inventory.outlet_id == row_outlet_id, Inventory.product_id == int(row["product_id"]),
                ).first()
                if existing:
                    existing.quantity = int(row["quantity"])
                else:
                    db.add(Inventory(
                        outlet_id=row_outlet_id, product_id=int(row["product_id"]),
                        quantity=int(row["quantity"]),
                    ))
            elif payload.dataset_type == "employees":
                db.add(Employee(
                    outlet_id=row_outlet_id, full_name=str(row["full_name"]),
                    designation=row.get("designation") or None, date_joined=row.get("date_joined") or None,
                ))
            inserted += 1
        except Exception as exc:
            skipped += 1
            errors.append(f"Row {i}: {exc}")

    db.commit()
    return CommitResult(dataset_type=payload.dataset_type, inserted=inserted, skipped=skipped, errors=errors[:20])
