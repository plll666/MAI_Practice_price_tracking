from typing import Any

from sqlalchemy import select

from src.celery.app import celery_app
from src.core.logger import logger
from src.database.database import SyncSessionLocal
from src.database.models import ProductLinks, PriceHistory, Subscriptions


@celery_app.task(bind=True, name="src.celery.tasks.check_price_alerts")
def check_price_alerts_task(self) -> dict[str, Any]:
    logger.info("Checking for price alerts")
    db = SyncSessionLocal()
    try:
        query = select(Subscriptions).where(Subscriptions.target_price.isnot(None))
        result = db.execute(query)
        subscriptions = result.scalars().all()

        alerts = []
        for sub in subscriptions:
            price_query = (
                select(PriceHistory.price)
                .join(ProductLinks)
                .where(
                    ProductLinks.product_id == sub.product_id,
                    PriceHistory.link_id == ProductLinks.id
                )
                .order_by(PriceHistory.parsed_at.desc())
                .limit(1)
            )
            price_res = db.execute(price_query)
            current_price = price_res.scalar_one_or_none()

            if current_price and current_price <= sub.target_price:
                alerts.append({
                    "subscription_id": sub.id,
                    "product_id": sub.product_id,
                    "current_price": float(current_price),
                    "target_price": float(sub.target_price)
                })

        logger.info(f"Found {len(alerts)} price alerts")
        return {"status": "success", "alerts": alerts}
    except Exception as e:
        db.rollback()
        logger.error(f"Error in check_price_alerts_task: {str(e)}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()