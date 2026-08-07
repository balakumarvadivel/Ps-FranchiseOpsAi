import pandas as pd
from app.services.data_validation import validate_dataset


def test_clean_dataset_scores_100():
    df = pd.DataFrame({
        "outlet_id": [1, 2, 3],
        "product_id": [1, 1, 2],
        "quantity": [5, 3, 2],
        "unit_price": [100.0, 200.0, 150.0],
        "sale_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
    })
    report = validate_dataset(df, "sales")
    assert report["valid"] is True
    assert report["data_quality_score"] == 100.0
    assert report["flagged_rows"] == 0


def test_missing_required_column_returns_invalid():
    df = pd.DataFrame({"outlet_id": [1], "product_id": [1]})  # missing quantity, unit_price, sale_date
    report = validate_dataset(df, "sales")
    assert report["valid"] is False
    assert "error" in report


def test_detects_missing_values():
    df = pd.DataFrame({
        "outlet_id": [1, 2, None],
        "product_id": [1, 1, 2],
        "quantity": [5, 3, 2],
        "unit_price": [100.0, 200.0, 150.0],
        "sale_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
    })
    report = validate_dataset(df, "sales")
    assert report["issues"]["missing_values"].get("outlet_id") == 1
    assert report["flagged_rows"] == 1
    assert report["data_quality_score"] < 100.0


def test_detects_duplicate_entries():
    df = pd.DataFrame({
        "outlet_id": [1, 1],
        "product_id": [1, 1],
        "quantity": [5, 5],
        "unit_price": [100.0, 100.0],
        "sale_date": ["2026-01-01", "2026-01-01"],
    })
    report = validate_dataset(df, "sales")
    assert report["issues"]["duplicate_entries"] == 1
    assert report["clean_rows"] == 1


def test_detects_invalid_prices():
    df = pd.DataFrame({
        "outlet_id": [1, 2],
        "product_id": [1, 1],
        "quantity": [5, 3],
        "unit_price": [-50.0, 100.0],
        "sale_date": ["2026-01-01", "2026-01-02"],
    })
    report = validate_dataset(df, "sales")
    assert report["issues"]["invalid_prices"].get("unit_price") == 1


def test_detects_invalid_inventory_quantity():
    df = pd.DataFrame({"outlet_id": [1, 2], "product_id": [1, 1], "quantity": [-5, 10]})
    report = validate_dataset(df, "inventory")
    assert report["issues"]["invalid_inventory"].get("quantity") == 1


def test_unknown_dataset_type_raises():
    df = pd.DataFrame({"a": [1]})
    try:
        validate_dataset(df, "unknown_type")
        assert False, "should have raised"
    except ValueError:
        pass
