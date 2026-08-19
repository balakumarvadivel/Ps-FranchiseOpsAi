from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.core.pagination import Pagination, paginate_with_headers
from app.database import get_db
from app.models.user import User
from app.models.marketing_audit import MarketingCampaign
from app.schemas.marketing import CampaignCreate, CampaignUpdate, CampaignOut, CustomerSegment
from app.services.ai.marketing_ai import (
    rank_campaigns, segment_customers, budget_optimization_recommendation,
)
from app.services.ai.recommender import recommend_campaign

router = APIRouter(prefix="/api/v1/marketing", tags=["Marketing Agent"])


def _to_out(c: MarketingCampaign) -> CampaignOut:
    return CampaignOut(
        id=c.id, outlet_id=c.outlet_id, name=c.name, channel=c.channel, campaign_type=c.campaign_type,
        start_date=c.start_date, end_date=c.end_date, budget=float(c.budget), ad_cost=float(c.ad_cost),
        revenue_generated=float(c.revenue_generated), customer_reach=c.customer_reach,
        leads=c.leads or 0, conversions=c.conversions or 0, conversion_rate_percent=c.conversion_rate_percent,
        coupon_redemptions=c.coupon_redemptions, status=c.status, roi_percent=c.roi_percent,
    )


@router.get("/campaigns", response_model=list[CampaignOut])
def list_campaigns(response: Response, outlet_id: Optional[int] = None, pagination: Pagination = Depends(),
                    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed = scoped_outlet_ids(current_user, db)
    query = db.query(MarketingCampaign)
    if allowed is not None:
        # Network-wide campaigns (outlet_id IS NULL) stay visible to everyone;
        # outlet-specific campaigns are filtered to what this user can see.
        query = query.filter(MarketingCampaign.outlet_id.in_(allowed) | MarketingCampaign.outlet_id.is_(None))
    if outlet_id:
        if allowed is not None and outlet_id not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")
        query = query.filter(MarketingCampaign.outlet_id == outlet_id)
    rows = paginate_with_headers(query.order_by(MarketingCampaign.start_date.desc()), pagination, response)
    return [_to_out(c) for c in rows]


@router.post("/campaigns", response_model=CampaignOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "regional_manager"))])
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    campaign = MarketingCampaign(**payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return _to_out(campaign)


@router.put("/campaigns/{campaign_id}", response_model=CampaignOut,
            dependencies=[Depends(require_role("admin", "regional_manager"))])
def update_campaign(campaign_id: int, payload: CampaignUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
    allowed = scoped_outlet_ids(current_user, db)
    if allowed is not None and campaign.outlet_id is not None and campaign.outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this campaign")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    return _to_out(campaign)


@router.get("/campaigns/ranking", response_model=list[CampaignOut])
def campaign_ranking(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    """AI feature: campaigns ranked by ROI, best to worst."""
    allowed = scoped_outlet_ids(current_user, db)
    if outlet_id and allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")
    ranked = rank_campaigns(db, outlet_id)
    if allowed is not None:
        ranked = [c for c in ranked if c.outlet_id is None or c.outlet_id in allowed]
    return [_to_out(c) for c in ranked]


@router.get("/campaigns/best-worst")
def campaign_best_worst(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """AI feature: Best Campaign / Poor Campaign."""
    allowed = scoped_outlet_ids(current_user, db)
    if outlet_id and allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")

    ranked = rank_campaigns(db, outlet_id)
    if allowed is not None:
        ranked = [c for c in ranked if c.outlet_id is None or c.outlet_id in allowed]
    if not ranked:
        return {"best": None, "worst": None}
    return {"best": _to_out(ranked[0]), "worst": _to_out(ranked[-1])}


@router.get("/customers/segments", response_model=list[CustomerSegment])
def customer_segments(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    """AI feature: Customer Segmentation."""
    allowed = scoped_outlet_ids(current_user, db)
    if outlet_id and allowed is not None and outlet_id not in allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this outlet")
    if outlet_id:
        return segment_customers(db, outlet_id)
    if allowed is None:
        return segment_customers(db, None)

    # No specific outlet requested but the user is scoped — aggregate segments
    # across just their allowed outlets instead of leaking the whole network.
    from collections import defaultdict
    totals = defaultdict(lambda: {"customer_count": 0, "spend_sum": 0.0})
    for oid in allowed:
        for seg in segment_customers(db, oid):
            totals[seg["segment"]]["customer_count"] += seg["customer_count"]
            totals[seg["segment"]]["spend_sum"] += seg["avg_spend"] * seg["customer_count"]
    return [
        {"segment": seg, "customer_count": t["customer_count"],
         "avg_spend": round(t["spend_sum"] / t["customer_count"], 2) if t["customer_count"] else 0}
        for seg, t in totals.items()
    ]


@router.get("/budget-optimization")
def budget_optimization(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI feature: Marketing Budget Optimization."""
    result = budget_optimization_recommendation(db)
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not enough campaign data across channels yet")
    return result


@router.get("/campaign-recommendation")
def campaign_recommendation(region: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI feature: Campaign Recommendation for a given region, based on best historical channel ROI."""
    ranked = rank_campaigns(db)
    if not ranked:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No campaign history to base a recommendation on")
    best = ranked[0]
    return recommend_campaign(best_channel=best.channel, region=region, expected_roi=best.roi_percent)
