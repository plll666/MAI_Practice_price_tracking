from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from src.core.hashid import encode_id


class ProductCreate(BaseModel):
    url: HttpUrl = Field(..., description="Ссылка на товар")
    target_price: Optional[float] = Field(None, description="Желаемая цена для уведомлений")


class TargetPriceUpdate(BaseModel):
    target_price: Optional[float] = Field(None, description="Желаемая цена")


class ProductResponse(BaseModel):
    id: str
    title: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    url: Optional[str] = None
    current_price: Optional[float] = 0.0
    target_price: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def transform_id_to_hash(cls, v):
        if v is None:
            return None
        if isinstance(v, int):
            return encode_id(v)
        if hasattr(v, 'id'):
            return encode_id(v.id)
        if isinstance(v, str):
            return v
        return str(v)


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    model_config = ConfigDict(from_attributes=True)


class ProductPriceResponse(BaseModel):
    id: str
    title: Optional[str] = None
    current_price: Optional[float] = None
    previous_price: Optional[float] = None
    shop: Optional[str] = None
    last_parsed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def transform_id_to_hash(cls, v):
        if v is None:
            return None
        if isinstance(v, int):
            return encode_id(v)
        if hasattr(v, 'id'):
            return encode_id(v.id)
        if isinstance(v, str):
            return v
        return str(v)


class ProductPriceListResponse(BaseModel):
    products: list[ProductPriceResponse]


class PricePoint(BaseModel):
    date: datetime
    price: float


class PriceHistoryResponse(BaseModel):
    product_id: str
    history: list[PricePoint]
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    avg_price: Optional[float] = None
    change_from_first: Optional[float] = None
    change_percent: Optional[float] = None

    @field_validator("product_id", mode="before")
    @classmethod
    def transform_product_id_to_hash(cls, v):
        if v is None:
            return None
        if isinstance(v, int):
            return encode_id(v)
        if hasattr(v, 'id'):
            return encode_id(v.id)
        if isinstance(v, str):
            return v
        return str(v)
