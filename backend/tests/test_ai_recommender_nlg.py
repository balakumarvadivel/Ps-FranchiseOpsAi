from app.services.ai.recommender import (
    recommend_for_outlet, recommend_for_inventory, recommend_stock_transfer, recommend_audit,
)
from app.services.ai.nlg_summary import generate_executive_summary


def test_recommend_for_outlet_flags_low_health():
    recs = recommend_for_outlet("Test Outlet", outlet_id=1, health_score=35, growth_percent=2)
    assert any(r.category == "finance" for r in recs)
    assert all(r.priority in ("critical", "high", "medium", "low") for r in recs)


def test_recommend_for_outlet_flags_negative_growth():
    recs = recommend_for_outlet("Test Outlet", outlet_id=1, health_score=85, growth_percent=-12)
    assert any(r.category == "marketing" for r in recs)


def test_recommend_for_outlet_healthy_outlet_no_recs():
    recs = recommend_for_outlet("Healthy Outlet", outlet_id=1, health_score=90, growth_percent=8)
    assert recs == []


def test_recommend_for_inventory_below_reorder():
    rec = recommend_for_inventory("Outlet A", 1, "Widget", quantity=5, reorder_level=20, avg_daily_sales=2)
    assert rec is not None
    assert rec.category == "inventory"


def test_recommend_for_inventory_healthy_stock_returns_none():
    rec = recommend_for_inventory("Outlet A", 1, "Widget", quantity=100, reorder_level=20, avg_daily_sales=2)
    assert rec is None


def test_recommend_stock_transfer_uses_min_quantity():
    rec = recommend_stock_transfer("Outlet A", "Outlet B", "Widget", surplus_qty=30, shortage_qty=10)
    assert "10" in rec.title  # transfers the smaller of surplus/shortage


def test_recommend_audit_priority_scales_with_overdue_days():
    mild = recommend_audit("Outlet A", 1, days_overdue=5)
    severe = recommend_audit("Outlet A", 1, days_overdue=45)
    assert mild.priority == "high"
    assert severe.priority == "critical"


def test_executive_summary_mentions_key_figures():
    text = generate_executive_summary(
        total_revenue=1_000_000, revenue_growth_percent=12.5, overall_health_score=82,
        best_outlet_name="Best Outlet", best_outlet_growth=20, worst_outlet_name="Worst Outlet",
        worst_outlet_health=40, profit_margin_percent=25, critical_outlet_count=1,
    )
    assert "Best Outlet" in text
    assert "Worst Outlet" in text
    assert "1 outlet" in text
