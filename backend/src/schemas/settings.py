from pydantic import BaseModel, Field
from typing import Optional


class SettingsUpdate(BaseModel):
    parse_interval: int = Field(..., ge=120, description="Интервал парсинга в секундах (мин. 120)")


class SettingsResponse(BaseModel):
    parse_interval: int


class NotificationSettingsUpdate(BaseModel):
    telegram_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None


class NotificationSettingsResponse(BaseModel):
    telegram_notifications: bool
    email_notifications: bool
    telegram_connected: bool


class TelegramLinkResponse(BaseModel):
    code: str
    link: str
    expires_in: int