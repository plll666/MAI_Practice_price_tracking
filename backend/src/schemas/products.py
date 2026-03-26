from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ProductCreate(BaseModel):
    url: HttpUrl = Field(..., description="Ссылка на товар")

class ProductResponse(BaseModel):
    id: int
    title: Optional[str]
    class Config:
        from_attributes = True