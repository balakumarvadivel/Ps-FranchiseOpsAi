from datetime import date, timedelta
from typing import Optional, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.inventory import Inventory, Product
from app.models.sales import Sale
from app.services.ai.recommender import recommend_for_inventory, Recommendation


def inventory_recommendation_objects(db: Session, outlet_id: Optional[int] = None) -> List[Recommendation]:
    query = db.query(Inventory).join(Product, Product.id == Inventory.product_id)
    if outlet_id:
        query = query.filter(Inventory.outlet_id == outlet_id)

    since = date.today() - timedelta(days=30)
    recommendations: List[Recommendation] = []

    for row in query.all():
        avg_daily_sales = (
            db.query(func.coalesce(func.sum(Sale.quantity), 0))
            .filter(Sale.product_id == row.product_id, Sale.outlet_id == row.outlet_id, Sale.sale_date >= since)
            .scalar() or 0
        ) / 30

        rec = recommend_for_inventory(
            outlet_name=row.outlet.name, outlet_id=row.outlet_id, product_name=row.product.name,
            quantity=row.quantity, reorder_level=row.product.reorder_level, avg_daily_sales=avg_daily_sales,
        )
        if rec:
            recommendations.append(rec)

    return recommendations
