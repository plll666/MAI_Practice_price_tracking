from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator
from typing import Optional
from src.core.hashid import encode_id

class ProductCreate(BaseModel):
    url: HttpUrl = Field(..., description="Ссылка на товар")

class ProductResponse(BaseModel):
    id: str
    title: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    current_price: Optional[float] = 0.0
    
    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def transform_id_to_hash(cls, v):
        if isinstance(v, int):
            return encode_id(v)
        return v

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    model_config = ConfigDict(from_attributes=True)