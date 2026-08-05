"""
Data Validation & Processing
------------------------------
Generic CSV/Excel validator + cleaner for the datasets a franchise operator
would realistically bulk-upload: sales, inventory, and employees. Each
dataset type has a small schema (required columns + which ones are dates /
prices / quantities), which drives every check below.

Data Quality Score (0-100): starts at 100 and loses points proportional to
the SHARE of rows affected by each issue type, weighted by how serious that
issue is (a missing value is recoverable; a duplicate or invalid price is
worse). This keeps the score meaningful whether you upload 50 rows or
50,000 — one bad row in a big file barely moves it, which is what you'd
expect from a real quality metric.
"""
from datetime import datetime
from typing import Optional

import pandas as pd

SCHEMAS = {
    "sales": {
        "required": ["outlet_id", "product_id", "quantity", "unit_price", "sale_date"],
        "date_cols": ["sale_date"],
        "price_cols": ["unit_price"],
        "qty_cols": ["quantity"],
        "dedupe_keys": ["outlet_id", "product_id", "sale_date", "quantity", "unit_price"],
    },
    "inventory": {
        "required": ["outlet_id", "product_id", "quantity"],
        "date_cols": [],
        "price_cols": [],
        "qty_cols": ["quantity"],
        "dedupe_keys": ["outlet_id", "product_id"],
    },
    "employees": {
        "required": ["outlet_id", "full_name", "date_joined"],
        "date_cols": ["date_joined"],
        "price_cols": [],
        "qty_cols": [],
        "dedupe_keys": ["outlet_id", "full_name", "date_joined"],
    },
}

PENALTY_WEIGHTS = {
    "missing_values": 15,
    "duplicate_entries": 20,
    "invalid_dates": 20,
    "invalid_prices": 25,
    "invalid_inventory": 25,
}


def read_upload(file_bytes: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(pd.io.common.BytesIO(file_bytes))
    return pd.read_csv(pd.io.common.BytesIO(file_bytes))


def _try_parse_date(value) -> bool:
    if pd.isna(value):
        return False
    try:
        pd.to_datetime(value)
        return True
    except (ValueError, TypeError):
        return False


def validate_dataset(df: pd.DataFrame, dataset_type: str) -> dict:
    if dataset_type not in SCHEMAS:
        raise ValueError(f"Unknown dataset_type '{dataset_type}'. Expected one of {list(SCHEMAS)}")

    schema = SCHEMAS[dataset_type]
    total_rows = len(df)
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing_required = [c for c in schema["required"] if c not in df.columns]
    if missing_required:
        return {
            "valid": False,
            "error": f"Missing required column(s): {', '.join(missing_required)}",
            "total_rows": total_rows,
            "data_quality_score": 0,
        }

    issues = {"missing_values": {}, "duplicate_entries": 0, "invalid_dates": {}, "invalid_prices": {}, "invalid_inventory": {}}
    suggestions = []
    row_flags = pd.Series(False, index=df.index)  # True = row has at least one problem

    # --- Missing values -------------------------------------------------
    for col in schema["required"]:
        missing_count = int(df[col].isna().sum())
        if missing_count:
            issues["missing_values"][col] = missing_count
            row_flags |= df[col].isna()
            suggestions.append(f"'{col}' has {missing_count} missing value(s) — fill with the column median/mode or drop those rows.")

    # --- Duplicate entries -------------------------------------------------
    dedupe_keys = [k for k in schema["dedupe_keys"] if k in df.columns]
    if dedupe_keys:
        dup_mask = df.duplicated(subset=dedupe_keys, keep="first")
        dup_count = int(dup_mask.sum())
        if dup_count:
            issues["duplicate_entries"] = dup_count
            row_flags |= dup_mask
            suggestions.append(f"{dup_count} duplicate row(s) found based on {', '.join(dedupe_keys)} — duplicates will be dropped, keeping the first occurrence.")

    # --- Invalid dates -------------------------------------------------
    for col in schema["date_cols"]:
        if col not in df.columns:
            continue
        invalid_mask = df[col].apply(lambda v: not _try_parse_date(v))
        invalid_count = int(invalid_mask.sum())
        if invalid_count:
            issues["invalid_dates"][col] = invalid_count
            row_flags |= invalid_mask
            suggestions.append(f"'{col}' has {invalid_count} unparseable date(s) — expected a standard date format (e.g. YYYY-MM-DD).")

    # --- Invalid prices -------------------------------------------------
    for col in schema["price_cols"]:
        if col not in df.columns:
            continue
        numeric = pd.to_numeric(df[col], errors="coerce")
        invalid_mask = numeric.isna() | (numeric <= 0)
        invalid_count = int(invalid_mask.sum())
        if invalid_count:
            issues["invalid_prices"][col] = invalid_count
            row_flags |= invalid_mask
            suggestions.append(f"'{col}' has {invalid_count} invalid price(s) (non-numeric or ≤ 0) — these rows need a manual price check.")

    # --- Invalid inventory / quantity -------------------------------------------------
    for col in schema["qty_cols"]:
        if col not in df.columns:
            continue
        numeric = pd.to_numeric(df[col], errors="coerce")
        invalid_mask = numeric.isna() | (numeric < 0)
        invalid_count = int(invalid_mask.sum())
        if invalid_count:
            issues["invalid_inventory"][col] = invalid_count
            row_flags |= invalid_mask
            suggestions.append(f"'{col}' has {invalid_count} invalid quantity value(s) (non-numeric or negative).")

    # --- Data Quality Score -------------------------------------------------
    score = 100.0
    if total_rows > 0:
        score -= (sum(issues["missing_values"].values()) / total_rows) * PENALTY_WEIGHTS["missing_values"]
        score -= (issues["duplicate_entries"] / total_rows) * PENALTY_WEIGHTS["duplicate_entries"]
        score -= (sum(issues["invalid_dates"].values()) / total_rows) * PENALTY_WEIGHTS["invalid_dates"]
        score -= (sum(issues["invalid_prices"].values()) / total_rows) * PENALTY_WEIGHTS["invalid_prices"]
        score -= (sum(issues["invalid_inventory"].values()) / total_rows) * PENALTY_WEIGHTS["invalid_inventory"]
    score = max(0.0, min(100.0, round(score, 1)))

    clean_df = df.loc[~row_flags].copy()
    if dedupe_keys:
        clean_df = clean_df.drop_duplicates(subset=dedupe_keys, keep="first")

    if not suggestions:
        suggestions.append("No issues detected — this dataset is ready to import as-is.")

    return {
        "valid": True,
        "dataset_type": dataset_type,
        "total_rows": total_rows,
        "clean_rows": len(clean_df),
        "flagged_rows": int(row_flags.sum()),
        "issues": issues,
        "cleaning_suggestions": suggestions,
        "data_quality_score": score,
        "cleaned_preview": clean_df.head(200).fillna("").to_dict(orient="records"),
        "cleaned_data": clean_df.fillna("").to_dict(orient="records"),
    }
