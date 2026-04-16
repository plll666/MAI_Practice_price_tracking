from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SummaryStats(BaseModel):
    total_products: int = 0
    total_shops: int = 0
    total_savings: float = 0.0
    avg_price_change: float = 0.0
    avg_price: float = 0.0
    min_price: float = 0.0
    max_price: float = 0.0


class ShopStats(BaseModel):
    shop: str
    count: int
    avg_change: float
    total_savings: float


class PriceTrendPoint(BaseModel):
    date: str
    avg_price: float
    min_price: float
    max_price: float


class TopChangeItem(BaseModel):
    product_id: str
    title: str
    image_url: Optional[str] = None
    shop: str
    current_price: float
    previous_price: float
    change: float
    change_percent: float
    savings: Optional[float] = None


class HistogramBucket(BaseModel):
    range_min: int
    range_max: int
    count: int
    label: str


class TimelineEvent(BaseModel):
    date: str
    product_id: str
    title: str
    price_from: float
    price_to: float
    change_percent: float
    is_drop: bool


class AnalyticsResponse(BaseModel):
    summary: SummaryStats
    by_shop: list[ShopStats] = []
    price_trend: list[PriceTrendPoint] = []
    top_drops: list[TopChangeItem] = []
    top_increases: list[TopChangeItem] = []
    price_histogram: list[HistogramBucket] = []
    changes_timeline: list[TimelineEvent] = []
