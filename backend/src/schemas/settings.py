from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    parse_interval: int = Field(..., ge=1, description="Интервал парсинга в часах")


class SettingsResponse(BaseModel):
    parse_interval: int