"""
Business Recommendation Engine
-------------------------------
Rule-based (transparent) recommendation generator. Each rule inspects a slice
of outlet/inventory/staff/marketing/audit data and — if its condition is
met — emits a recommendation with priority, reason, impact and a confidence
score. This mirrors the "Smart AI Recommendations" and "Business
Recommendation Engine" sections of the spec, and stays easy to unit test
since each rule is a pure function of its inputs.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Recommendation:
    title: str
    description: str
    priority: str          # critical | high | medium | low
    category: str          # inventory | marketing | staff | audit | finance
    impact: str             # short human-readable expected impact
    confidence: float       # 0-100
    outlet_id: Optional[int] = None


def _priority_from_score(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def recommend_for_outlet(outlet_name: str, outlet_id: int, health_score: float, growth_percent: float) -> List[Recommendation]:
    recs = []
    if health_score < 50:
        urgency = (50 - health_score) * 2
        recs.append(Recommendation(
            title=f"Prioritize recovery plan for {outlet_name}",
            description=f"Health score is {health_score}/100, below the critical threshold. "
                         f"Focus on the lowest sub-metrics (see health breakdown) first.",
            priority=_priority_from_score(60 + urgency),
            category="finance",
            impact="Prevents further revenue and reputation loss",
            confidence=88.0,
            outlet_id=outlet_id,
        ))
    if growth_percent < -5:
        recs.append(Recommendation(
            title=f"Launch a win-back campaign for {outlet_name}",
            description=f"Revenue declined {abs(growth_percent)}% versus the previous period.",
            priority="high" if growth_percent < -10 else "medium",
            category="marketing",
            impact="Typically recovers 3-6% of lost revenue within a month",
            confidence=72.0,
            outlet_id=outlet_id,
        ))
    return recs


def recommend_for_inventory(outlet_name: str, outlet_id: int, product_name: str,
                              quantity: int, reorder_level: int, avg_daily_sales: float) -> Optional[Recommendation]:
    if quantity <= reorder_level:
        days_left = round(quantity / avg_daily_sales, 1) if avg_daily_sales > 0 else None
        urgency_score = 90 if quantity == 0 else 70 if quantity < reorder_level / 2 else 50
        return Recommendation(
            title=f"Reorder {product_name} at {outlet_name}",
            description=(
                f"Current stock ({quantity}) is at or below the reorder level ({reorder_level})."
                + (f" Estimated {days_left} days of stock remaining." if days_left else "")
            ),
            priority=_priority_from_score(urgency_score),
            category="inventory",
            impact="Avoids stockouts on an active-selling product",
            confidence=85.0,
            outlet_id=outlet_id,
        )
    return None


def recommend_stock_transfer(from_outlet: str, to_outlet: str, product_name: str,
                               surplus_qty: int, shortage_qty: int) -> Recommendation:
    transfer_qty = min(surplus_qty, shortage_qty)
    return Recommendation(
        title=f"Transfer {transfer_qty} units of {product_name}: {from_outlet} → {to_outlet}",
        description=f"{from_outlet} is overstocked while {to_outlet} is running low on the same SKU.",
        priority="medium",
        category="inventory",
        impact="Reduces holding cost and prevents a stockout without new purchasing",
        confidence=80.0,
    )


def recommend_audit(outlet_name: str, outlet_id: int, days_overdue: int) -> Recommendation:
    return Recommendation(
        title=f"Schedule overdue audit for {outlet_name}",
        description=f"This outlet's audit is {days_overdue} days overdue.",
        priority="critical" if days_overdue > 30 else "high",
        category="audit",
        impact="Reduces compliance and fraud risk exposure",
        confidence=95.0,
        outlet_id=outlet_id,
    )


def recommend_campaign(best_channel: str, region: str, expected_roi: float) -> Recommendation:
    return Recommendation(
        title=f"Launch a {best_channel} campaign in {region}",
        description=f"Historical {best_channel} campaigns in similar regions returned ~{expected_roi}% ROI.",
        priority="medium",
        category="marketing",
        impact=f"Projected ROI of ~{expected_roi}%",
        confidence=68.0,
    )
