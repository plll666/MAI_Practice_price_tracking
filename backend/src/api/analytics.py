from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.products import get_current_user
from src.database.database import get_db
from src.repositories.analytics_repository import AnalyticsRepository
from src.services.analytics_service import AnalyticsService
from src.schemas.analytics import AnalyticsResponse
from src.core.logger import logger

router = APIRouter(prefix="", tags=["Analytics"])


async def get_analytics_service(db: AsyncSession = Depends(get_db)):
    repo = AnalyticsRepository(db)
    return AnalyticsService(repo)


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    days: int = Query(default=30, ge=7, le=365, description="Количество дней для анализа"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить полную аналитику по товарам пользователя.
    
    Включает:
    - Сводную статистику
    - Распределение по магазинам
    - Динамику цен
    - ТОП снижений и повышений
    - Гистограмму цен
    - Timeline изменений
    """
    logger.info(f"Аналитика: пользователь '{current_user.login}' запрашивает данные за {days} дней")
    
    service = await get_analytics_service(db)
    analytics = await service.get_full_analytics(current_user.id, days)
    
    logger.info(f"Аналитика: найдено {analytics.summary.total_products} товаров, {analytics.summary.total_shops} магазинов")
    
    return analytics
