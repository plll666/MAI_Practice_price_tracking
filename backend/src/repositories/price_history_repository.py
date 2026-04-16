from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Products, ProductLinks, PriceHistory, Subscriptions, Shops
from src.core.logger import logger


class PriceHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_products_with_prices(self, user_id: int) -> list[dict]:
        """Получить товары пользователя с последними ценами."""
        try:
            subquery = (
                select(
                    PriceHistory.link_id,
                    func.max(PriceHistory.parsed_at).label("max_parsed")
                )
                .group_by(PriceHistory.link_id)
                .subquery()
            )

            latest_prices_subquery = (
                select(PriceHistory)
                .join(subquery, 
                    (PriceHistory.link_id == subquery.c.link_id) & 
                    (PriceHistory.parsed_at == subquery.c.max_parsed)
                )
                .subquery()
            )

            previous_prices_subquery = (
                select(
                    PriceHistory.link_id,
                    func.max(PriceHistory.parsed_at).label("prev_parsed")
                )
                .join(subquery, PriceHistory.link_id == subquery.c.link_id)
                .where(PriceHistory.parsed_at < latest_prices_subquery.c.parsed_at)
                .group_by(PriceHistory.link_id)
                .subquery()
            )

            query = (
                select(
                    Products.id,
                    Products.title,
                    latest_prices_subquery.c.price.label("current_price"),
                    previous_prices_subquery.c.price.label("previous_price"),
                    Shops.name.label("shop"),
                    latest_prices_subquery.c.parsed_at.label("last_parsed_at")
                )
                .join(ProductLinks, ProductLinks.product_id == Products.id)
                .join(Subscriptions, Subscriptions.product_id == Products.id)
                .join(latest_prices_subquery, latest_prices_subquery.c.link_id == ProductLinks.id)
                .outerjoin(previous_prices_subquery, previous_prices_subquery.c.link_id == ProductLinks.id)
                .join(Shops, Shops.id == ProductLinks.shop_id)
                .where(Subscriptions.user_id == user_id)
                .distinct(Products.id)
            )

            result = await self.db.execute(query)
            rows = result.all()

            return [
                {
                    "id": row.id,
                    "title": row.title,
                    "current_price": float(row.current_price) if row.current_price else None,
                    "previous_price": float(row.previous_price) if row.previous_price else None,
                    "shop": row.shop,
                    "last_parsed_at": row.last_parsed_at
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Ошибка получения цен товаров: {e}")
            return []

    async def get_product_price_history(
        self, 
        product_id: int, 
        days: int = 30
    ) -> dict:
        """Получить историю цен товара за N дней."""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)

            query = (
                select(PriceHistory)
                .join(ProductLinks, ProductLinks.id == PriceHistory.link_id)
                .where(
                    ProductLinks.product_id == product_id,
                    PriceHistory.parsed_at >= since_date
                )
                .order_by(PriceHistory.parsed_at.asc())
            )

            result = await self.db.execute(query)
            history_records = result.scalars().all()

            history = [
                {
                    "date": record.parsed_at,
                    "price": float(record.price)
                }
                for record in history_records
            ]

            if not history:
                return {
                    "product_id": product_id,
                    "history": [],
                    "min_price": None,
                    "max_price": None,
                    "avg_price": None,
                    "change_from_first": None,
                    "change_percent": None
                }

            prices = [h["price"] for h in history]
            first_price = history[0]["price"] if history else None
            last_price = history[-1]["price"] if history else None
            
            change = None
            change_percent = None
            if first_price and last_price and first_price != 0:
                change = last_price - first_price
                change_percent = (change / first_price) * 100

            return {
                "product_id": product_id,
                "history": history,
                "min_price": min(prices) if prices else None,
                "max_price": max(prices) if prices else None,
                "avg_price": sum(prices) / len(prices) if prices else None,
                "change_from_first": change,
                "change_percent": change_percent
            }
        except Exception as e:
            logger.error(f"Ошибка получения истории цен: {e}")
            return {
                "product_id": product_id,
                "history": [],
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "change_from_first": None,
                "change_percent": None
            }

    async def get_current_price(self, product_id: int) -> Optional[float]:
        """Получить текущую цену товара."""
        try:
            query = (
                select(PriceHistory.price)
                .join(ProductLinks, ProductLinks.id == PriceHistory.link_id)
                .where(ProductLinks.product_id == product_id)
                .order_by(PriceHistory.parsed_at.desc())
                .limit(1)
            )
            result = await self.db.execute(query)
            price = result.scalar_one_or_none()
            return float(price) if price else None
        except Exception as e:
            logger.error(f"Ошибка получения текущей цены: {e}")
            return None

    async def add_price_record(self, link_id: int, price: float) -> bool:
        """Добавить запись о цене."""
        try:
            new_record = PriceHistory(link_id=link_id, price=price)
            self.db.add(new_record)
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления цены: {e}")
            await self.db.rollback()
            return False
