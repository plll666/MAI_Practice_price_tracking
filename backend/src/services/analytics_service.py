from src.repositories.analytics_repository import AnalyticsRepository
from src.schemas.analytics import (
    AnalyticsResponse,
    SummaryStats,
    ShopStats,
    PriceTrendPoint,
    TopChangeItem,
    HistogramBucket,
    TimelineEvent
)
from src.core.logger import logger


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    async def get_full_analytics(self, user_id: int, days: int = 30) -> AnalyticsResponse:
        """Получить полную аналитику для пользователя."""
        logger.info(f"Получение аналитики для пользователя {user_id} за {days} дней")
        
        try:
            summary = await self.repo.get_summary_stats(user_id, days)
        except Exception as e:
            logger.error(f"Ошибка получения summary: {e}")
            await self.repo.db.rollback()
            summary = {
                "total_products": 0, "total_shops": 0, "total_savings": 0.0,
                "avg_price_change": 0.0, "avg_price": 0.0, "min_price": 0.0, "max_price": 0.0
            }
        
        try:
            by_shop = await self.repo.get_products_by_shop(user_id)
        except Exception as e:
            logger.error(f"Ошибка получения by_shop: {e}")
            await self.repo.db.rollback()
            by_shop = []
        
        try:
            price_trend = await self.repo.get_price_trend(user_id, days)
        except Exception as e:
            logger.error(f"Ошибка получения price_trend: {e}")
            await self.repo.db.rollback()
            price_trend = []
        
        try:
            top_drops = await self.repo.get_top_changes(user_id, days, limit=10, direction="drops")
        except Exception as e:
            logger.error(f"Ошибка получения top_drops: {e}")
            await self.repo.db.rollback()
            top_drops = []
        
        try:
            top_increases = await self.repo.get_top_changes(user_id, days, limit=10, direction="increases")
        except Exception as e:
            logger.error(f"Ошибка получения top_increases: {e}")
            await self.repo.db.rollback()
            top_increases = []
        
        try:
            price_histogram = await self.repo.get_price_histogram(user_id)
        except Exception as e:
            logger.error(f"Ошибка получения price_histogram: {e}")
            await self.repo.db.rollback()
            price_histogram = []
        
        try:
            changes_timeline = await self.repo.get_changes_timeline(user_id, days, limit=50)
        except Exception as e:
            logger.error(f"Ошибка получения changes_timeline: {e}")
            await self.repo.db.rollback()
            changes_timeline = []
        
        try:
            return AnalyticsResponse(
                summary=SummaryStats(**summary),
                by_shop=[ShopStats(**shop) for shop in by_shop],
                price_trend=[PriceTrendPoint(**point) for point in price_trend],
                top_drops=[TopChangeItem(**item) for item in top_drops],
                top_increases=[TopChangeItem(**item) for item in top_increases],
                price_histogram=[HistogramBucket(**bucket) for bucket in price_histogram],
                changes_timeline=[TimelineEvent(**event) for event in changes_timeline]
            )
        except Exception as e:
            logger.error(f"Ошибка формирования ответа: {e}")
            return AnalyticsResponse(
                summary=SummaryStats(**summary),
                by_shop=[],
                price_trend=[],
                top_drops=[],
                top_increases=[],
                price_histogram=[],
                changes_timeline=[]
            )
