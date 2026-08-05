from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role, scoped_outlet_ids
from app.database import get_db
from app.models.user import User
from app.models.marketing_audit import MarketingCampaign
from app.schemas.marketing import CampaignCreate, CampaignUpdate, CampaignOut, CustomerSegment
from app.services.ai.marketing_ai import (
    rank_campaigns, best_and_worst_campaign, segment_customers, budget_optimization_recommendation,
)
from app.services.ai.recommender import recommend_campaign

router = APIRouter(prefix="/api/v1/marketing", tags=["Marketing Agent"])


def _to_out(c: MarketingCampaign) -> CampaignOut:
    return CampaignOut(
        id=c.id, outlet_id=c.outlet_id, name=c.name, channel=c.channel, start_date=c.start_date,
        end_date=c.end_date, budget=float(c.budget), ad_cost=float(c.ad_cost),
        revenue_generated=float(c.revenue_generated), customer_reach=c.customer_reach,
        coupon_redemptions=c.coupon_redemptions, status=c.status, roi_percent=c.roi_percent,
    )


@router.get("/campaigns", response_model=list[CampaignOut])
def list_campaigns(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    query = db.query(MarketingCampaign)
    if outlet_id:
        query = query.filter(MarketingCampaign.outlet_id == outlet_id)
    return [_to_out(c) for c in query.order_by(MarketingCampaign.start_date.desc()).all()]


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
def update_campaign(campaign_id: int, payload: CampaignUpdate, db: Session = Depends(get_db)):
    campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaign not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    return _to_out(campaign)


@router.get("/campaigns/ranking", response_model=list[CampaignOut])
def campaign_ranking(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    """AI feature: campaigns ranked by ROI, best to worst."""
    return [_to_out(c) for c in rank_campaigns(db, outlet_id)]


@router.get("/campaigns/best-worst")
def campaign_best_worst(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """AI feature: Best Campaign / Poor Campaign."""
    result = best_and_worst_campaign(db, outlet_id)
    return {
        "best": _to_out(result["best"]) if result["best"] else None,
        "worst": _to_out(result["worst"]) if result["worst"] else None,
    }


@router.get("/customers/segments", response_model=list[CustomerSegment])
def customer_segments(outlet_id: Optional[int] = None, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    """AI feature: Customer Segmentation."""
    return segment_customers(db, outlet_id)


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
