"""
Marketing Agent — AI Layer
--------------------------
  best/poor campaign      -> simple ranking by ROI %
  customer segmentation   -> rule-based RFM-lite using visit_count + total_spent + recency
  budget optimization     -> reallocate a % of budget from the lowest-ROI channel
                              to the highest-ROI channel
"""
from datetime import date, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.models.marketing_audit import MarketingCampaign
from app.models.sales import Customer


def rank_campaigns(db: Session, outlet_id: int | None = None) -> List[MarketingCampaign]:
    query = db.query(MarketingCampaign)
    if outlet_id:
        query = query.filter(MarketingCampaign.outlet_id == outlet_id)
    campaigns = query.all()
    return sorted(campaigns, key=lambda c: c.roi_percent, reverse=True)


def best_and_worst_campaign(db: Session, outlet_id: int | None = None) -> dict:
    ranked = rank_campaigns(db, outlet_id)
    if not ranked:
        return {"best": None, "worst": None}
    return {"best": ranked[0], "worst": ranked[-1]}


def segment_customers(db: Session, outlet_id: int | None = None) -> List[dict]:
    """
    Rule-based RFM-lite segmentation:
      VIP      -> visit_count >= 10 and total_spent >= 5000
      Regular  -> visit_count >= 3
      New      -> first_visit within last 30 days
      At-risk  -> last_visit more than 60 days ago (was active, has gone quiet)
    """
    query = db.query(Customer)
    if outlet_id:
        query = query.filter(Customer.outlet_id == outlet_id)
    customers = query.all()

    today = date.today()
    buckets = {"VIP": [], "Regular": [], "New": [], "At-risk": []}

    for c in customers:
        spent = float(c.total_spent or 0)
        visits = c.visit_count or 0

        if c.last_visit and (today - c.last_visit).days > 60:
            buckets["At-risk"].append(c)
        elif visits >= 10 and spent >= 5000:
            buckets["VIP"].append(c)
        elif c.first_visit and (today - c.first_visit).days <= 30:
            buckets["New"].append(c)
        elif visits >= 3:
            buckets["Regular"].append(c)
        else:
            buckets.setdefault("Occasional", []).append(c)

    result = []
    for segment, members in buckets.items():
        if not members:
            continue
        avg_spend = sum(float(m.total_spent or 0) for m in members) / len(members)
        result.append({"segment": segment, "customer_count": len(members), "avg_spend": round(avg_spend, 2)})
    return result


def budget_optimization_recommendation(db: Session) -> dict | None:
    campaigns = db.query(MarketingCampaign).filter(MarketingCampaign.status.in_(["active", "completed"])).all()
    if len(campaigns) < 2:
        return None

    by_channel: dict[str, list] = {}
    for c in campaigns:
        by_channel.setdefault(c.channel, []).append(c)

    channel_roi = {
        channel: sum(c.roi_percent for c in items) / len(items)
        for channel, items in by_channel.items()
    }
    if len(channel_roi) < 2:
        return None

    best_channel = max(channel_roi, key=channel_roi.get)
    worst_channel = min(channel_roi, key=channel_roi.get)
    if best_channel == worst_channel:
        return None

    return {
        "move_budget_from": worst_channel,
        "move_budget_to": best_channel,
        "from_roi_percent": round(channel_roi[worst_channel], 1),
        "to_roi_percent": round(channel_roi[best_channel], 1),
        "suggested_shift_percent": 20,
        "reason": f"{best_channel} campaigns are averaging {round(channel_roi[best_channel] - channel_roi[worst_channel], 1)} "
                  f"points higher ROI than {worst_channel}.",
    }
