"""
API эндпоинты настроек для управления интервалами парсинга пользователей.

Предоставляет эндпоинты для получения и обновления интервалов парсинга продуктов пользователей.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.database.models import Users
from src.schemas.settings import SettingsUpdate, SettingsResponse
from src.core.logger import logger
from src.api.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post(
    "/parse-interval",
    response_model=SettingsResponse,
    summary="Обновить интервал парсинга пользователя",
    description="Обновить интервал (в часах) для парсинга продуктов текущего пользователя."
)
async def update_parse_interval(
    settings_data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
) -> SettingsResponse:
    """Обновить интервал парсинга для текущего пользователя."""
    current_user.parse_interval = settings_data.parse_interval
    await db.commit()
    await db.refresh(current_user)
    
    logger.info(f"Интервал парсинга для пользователя {current_user.login} обновлен до {settings_data.parse_interval} часов")
    
    return SettingsResponse(parse_interval=current_user.parse_interval)


@router.get(
    "/parse-interval",
    response_model=SettingsResponse,
    summary="Получить интервал парсинга пользователя",
    description="Получить текущий интервал парсинга для аутентифицированного пользователя."
)
async def get_parse_interval(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
) -> SettingsResponse:
    """Получить интервал парсинга для текущего пользователя."""
    return SettingsResponse(parse_interval=current_user.parse_interval or 1)