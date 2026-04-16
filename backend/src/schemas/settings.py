from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    parse_interval: int = Field(..., ge=120, description="Интервал парсинга в секундах (мин. 120)")


class SettingsResponse(BaseModel):
    parse_interval: int