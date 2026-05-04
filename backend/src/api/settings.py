"""
API эндпоинты настроек для управления интервалами парсинга пользователей.

Предоставляет эндпоинты для получения и обновления интервалов парсинга продуктов пользователей.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import string
import random

from src.database.database import get_db
from src.database.models import Users
from src.schemas.settings import SettingsUpdate, SettingsResponse, NotificationSettingsUpdate, NotificationSettingsResponse, TelegramLinkResponse
from src.core.logger import logger
from src.api.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post(
    "/parse-interval",
    response_model=SettingsResponse,
    summary="Обновить интервал парсинга пользователя",
    description="Обновить интервал (в секундах) для парсинга продуктов текущего пользователя."
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
    
    logger.info(f"Интервал парсинга для пользователя {current_user.login} обновлен до {settings_data.parse_interval} секунд")
    
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
    return SettingsResponse(parse_interval=current_user.parse_interval or 3600)


@router.post(
    "/notifications",
    response_model=NotificationSettingsResponse,
    summary="Обновить настройки уведомлений",
    description="Обновить настройки уведомлений пользователя."
)
async def update_notification_settings(
    settings_data: NotificationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
) -> NotificationSettingsResponse:
    """Обновить настройки уведомлений."""
    if settings_data.telegram_notifications is not None:
        current_user.telegram_notifications_enabled = settings_data.telegram_notifications
    if settings_data.email_notifications is not None:
        current_user.email_notifications_enabled = settings_data.email_notifications

    await db.commit()
    await db.refresh(current_user)

    telegram_connected = bool(current_user.chat_id)

    logger.info(f"Notification settings updated for user {current_user.login}")

    return NotificationSettingsResponse(
        telegram_notifications=current_user.telegram_notifications_enabled,
        email_notifications=current_user.email_notifications_enabled,
        telegram_connected=telegram_connected
    )


@router.get(
    "/notifications",
    response_model=NotificationSettingsResponse,
    summary="Получить настройки уведомлений",
    description="Получить текущие настройки уведомлений пользователя."
)
async def get_notification_settings(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
) -> NotificationSettingsResponse:
    """Получить настройки уведомлений."""
    telegram_connected = bool(current_user.chat_id)

    return NotificationSettingsResponse(
        telegram_notifications=current_user.telegram_notifications_enabled,
        email_notifications=current_user.email_notifications_enabled,
        telegram_connected=telegram_connected
    )


@router.post(
    "/telegram/link-code",
    response_model=TelegramLinkResponse,
    summary="Сгенерировать код привязки Telegram",
    description="Создать временный код для привязки Telegram аккаунта."
)
async def generate_linking_code(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
) -> TelegramLinkResponse:
    """Сгенерировать код для привязки Telegram."""
    code = ''.join(random.choices(string.digits, k=6))

    current_user.telegram_linking_code = code
    current_user.telegram_linking_code_expires = datetime.utcnow() + timedelta(minutes=5)
    await db.commit()

    bot_username = "mai_pric_trackerbot"
    link = f"https://t.me/{bot_username}"

    logger.info(f"Telegram linking code generated for user {current_user.login}")

    return TelegramLinkResponse(
        code=code,
        link=link,
        expires_in=300
    )


@router.get(
    "/telegram/status",
    summary="Проверить статус подключения Telegram",
    description="Проверить, подключен ли Telegram к аккаунту."
)
async def get_telegram_status(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
) -> dict:
    """Проверить статус подключения Telegram."""
    return {
        "connected": bool(current_user.chat_id),
        "chat_id": current_user.chat_id if current_user.chat_id else None
    }