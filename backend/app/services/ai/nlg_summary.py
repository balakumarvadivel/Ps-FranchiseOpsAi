"""
Natural Language AI Summary
----------------------------
Template-based NLG: structured numeric inputs are filled into professionally
worded sentence templates. This is deliberately not a call to a hosted LLM
(no network dependency, fully deterministic, explainable in a viva) — but the
function signature is generic enough to swap in an LLM call later if desired.
"""
from typing import Optional


def generate_executive_summary(
    total_revenue: float,
    revenue_growth_percent: float,
    overall_health_score: float,
    best_outlet_name: str,
    best_outlet_growth: float,
    worst_outlet_name: str,
    worst_outlet_health: float,
    profit_margin_percent: float,
    critical_outlet_count: int,
) -> str:
    trend_word = "grew" if revenue_growth_percent >= 0 else "declined"
    health_word = "healthy" if overall_health_score >= 75 else "stable" if overall_health_score >= 50 else "at risk"

    summary = (
        f"The franchise network generated ₹{total_revenue:,.0f} in revenue this period, "
        f"which {trend_word} {abs(revenue_growth_percent):.1f}% versus the previous period. "
        f"Overall franchise health is {health_word} at {overall_health_score:.0f}/100. "
        f"{best_outlet_name} is the top performer, growing {best_outlet_growth:.1f}%, while "
        f"{worst_outlet_name} is the weakest outlet with a health score of {worst_outlet_health:.0f}/100. "
        f"Profit margin stands at {profit_margin_percent:.1f}%. "
    )

    if critical_outlet_count > 0:
        summary += (
            f"{critical_outlet_count} outlet{'s' if critical_outlet_count != 1 else ''} "
            f"{'are' if critical_outlet_count != 1 else 'is'} currently in critical condition and need immediate attention."
        )
    else:
        summary += "No outlets are currently in critical condition."

    return summary
