from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import delete

from src.celery.app import celery_app
from src.core.logger import logger
from src.database.database import SyncSessionLocal
from src.database.models import PriceHistory


@celery_app.task(bind=True, name="src.celery.tasks.cleanup_old_prices")
def cleanup_old_prices_task(self, days: int = 30) -> dict[str, Any]:
    logger.info(f"Cleaning up prices older than {days} days")
    db = SyncSessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = db.execute(
            delete(PriceHistory).where(PriceHistory.parsed_at < cutoff_date)
        )
        db.commit()
        deleted_count = result.rowcount
        logger.info(f"Deleted {deleted_count} old price records")
        return {"status": "success", "deleted_count": deleted_count}
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning up prices: {str(e)}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()