from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Products, ProductLinks, PriceHistory, Subscriptions, Shops
from src.core.hashid import encode_id


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_product_ids(self, user_id: int) -> list[int]:
        """Получить список ID товаров пользователя."""
        query = (
            select(Products.id)
            .join(Subscriptions, Subscriptions.product_id == Products.id)
            .where(Subscriptions.user_id == user_id)
        )
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def get_summary_stats(self, user_id: int, days: int = None) -> dict:
        """Получить сводную статистику (без фильтра по дате)."""
        product_ids = await self.get_user_product_ids(user_id)
        if not product_ids:
            return {
                "total_products": 0,
                "total_shops": 0,
                "total_savings": 0.0,
                "avg_price_change": 0.0,
                "avg_price": 0.0,
                "min_price": 0.0,
                "max_price": 0.0
            }

        products_query = (
            select(
                func.count(func.distinct(Products.id)).label("total_products"),
                func.count(func.distinct(Shops.id)).label("total_shops"),
                func.avg(PriceHistory.price).label("avg_price"),
                func.min(PriceHistory.price).label("min_price"),
                func.max(PriceHistory.price).label("max_price")
            )
            .select_from(Products)
            .join(ProductLinks, ProductLinks.product_id == Products.id)
            .join(Shops, Shops.id == ProductLinks.shop_id)
            .join(PriceHistory, PriceHistory.link_id == ProductLinks.id)
            .join(Subscriptions, Subscriptions.product_id == Products.id)
            .where(Subscriptions.user_id == user_id)
        )
        result = await self.db.execute(products_query)
        row = result.one()

        price_diff_subquery = (
            select(
                Products.id.label("product_id"),
                (func.max(PriceHistory.price) - func.min(PriceHistory.price)).label("diff")
            )
            .select_from(Products)
            .join(ProductLinks, ProductLinks.product_id == Products.id)
            .join(PriceHistory, PriceHistory.link_id == ProductLinks.id)
            .join(Subscriptions, Subscriptions.product_id == Products.id)
            .where(Subscriptions.user_id == user_id)
            .group_by(Products.id)
            .subquery()
        )

        savings_query = (
            select(func.sum(func.coalesce(price_diff_subquery.c.diff, 0)).label("total_savings"))
            .select_from(price_diff_subquery)
        )
        savings_result = await self.db.execute(savings_query)
        savings_row = savings_result.one()
        total_savings = float(savings_row.total_savings or 0) if savings_row else 0.0

        return {
            "total_products": row.total_products or 0,
            "total_shops": row.total_shops or 0,
            "total_savings": abs(total_savings),
            "avg_price_change": 0.0,
            "avg_price": float(row.avg_price or 0),
            "min_price": float(row.min_price or 0),
            "max_price": float(row.max_price or 0)
        }

    async def get_products_by_shop(self, user_id: int) -> list[dict]:
        """Получить статистику по магазинам."""
        query = (
            select(
                Shops.name.label("shop"),
                func.count(func.distinct(Products.id)).label("count")
            )
            .select_from(Products)
            .join(ProductLinks, ProductLinks.product_id == Products.id)
            .join(Shops, Shops.id == ProductLinks.shop_id)
            .join(Subscriptions, Subscriptions.product_id == Products.id)
            .where(Subscriptions.user_id == user_id)
            .group_by(Shops.name)
            .order_by(desc("count"))
        )
        result = await self.db.execute(query)
        
        return [
            {
                "shop": row.shop,
                "count": row.count,
                "avg_change": 0.0,
                "total_savings": 0.0
            }
            for row in result.all()
        ]

    async def get_price_trend(self, user_id: int, days: int) -> list[dict]:
        """Получить динамику цен по дням."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(
                func.date(PriceHistory.parsed_at).label("date"),
                func.avg(PriceHistory.price).label("avg_price"),
                func.min(PriceHistory.price).label("min_price"),
                func.max(PriceHistory.price).label("max_price")
            )
            .select_from(Products)
            .join(ProductLinks, ProductLinks.product_id == Products.id)
            .join(PriceHistory, PriceHistory.link_id == ProductLinks.id)
            .join(Subscriptions, Subscriptions.product_id == Products.id)
            .where(
                Subscriptions.user_id == user_id,
                PriceHistory.parsed_at >= since_date
            )
            .group_by(func.date(PriceHistory.parsed_at))
            .order_by("date")
        )
        result = await self.db.execute(query)
        
        return [
            {
                "date": str(row.date),
                "avg_price": float(row.avg_price or 0),
                "min_price": float(row.min_price or 0),
                "max_price": float(row.max_price or 0)
            }
            for row in result.all()
        ]

    async def get_top_changes(self, user_id: int, days: int, limit: int = 10, direction: str = "drops") -> list[dict]:
        """Получить топ изменений цен (первая цена за период vs последняя)."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        price_range_subquery = (
            select(
                PriceHistory.link_id,
                func.min(PriceHistory.parsed_at).label("first_date"),
                func.max(PriceHistory.parsed_at).label("last_date")
            )
            .where(PriceHistory.parsed_at >= since_date)
            .group_by(PriceHistory.link_id)
            .subquery()
        )
        
        first_prices = (
            select(
                PriceHistory.link_id,
                PriceHistory.price
            )
            .join(price_range_subquery,
                (PriceHistory.link_id == price_range_subquery.c.link_id) &
                (PriceHistory.parsed_at == price_range_subquery.c.first_date))
            .subquery()
        )
        
        last_prices = (
            select(
                PriceHistory.link_id,
                PriceHistory.price
            )
            .join(price_range_subquery,
                (PriceHistory.link_id == price_range_subquery.c.link_id) &
                (PriceHistory.parsed_at == price_range_subquery.c.last_date))
            .subquery()
        )
        
        query = (
            select(
                Products.id,
                Products.title,
                Products.image_url,
                Shops.name.label("shop"),
                first_prices.c.price.label("first_price"),
                last_prices.c.price.label("last_price")
            )
            .select_from(Products)
            .join(ProductLinks, ProductLinks.product_id == Products.id)
            .join(Shops, Shops.id == ProductLinks.shop_id)
            .join(first_prices, first_prices.c.link_id == ProductLinks.id)
            .join(last_prices, last_prices.c.link_id == ProductLinks.id)
            .join(Subscriptions, Subscriptions.product_id == Products.id)
            .where(Subscriptions.user_id == user_id)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        changes = []
        for row in rows:
            first_price = float(row.first_price)
            last_price = float(row.last_price)
            
            if first_price > 0:
                change = last_price - first_price
                change_percent = (change / first_price) * 100
                savings = first_price - last_price if last_price < first_price else 0
                
                changes.append({
                    "product_id": encode_id(row.id),
                    "title": row.title,
                    "image_url": row.image_url,
                    "shop": row.shop,
                    "current_price": last_price,
                    "previous_price": first_price,
                    "change": change,
                    "change_percent": float(change_percent),
                    "savings": float(savings) if savings > 0 else 0.0
                })
        
        if direction == "drops":
            changes.sort(key=lambda x: x["change_percent"])
        else:
            changes.sort(key=lambda x: x["change_percent"], reverse=True)
        
        return changes[:limit]

    async def get_price_histogram(self, user_id: int) -> list[dict]:
        """Получить гистограмму цен."""
        query = (
            select(
                func.max(PriceHistory.price).label("max_price")
            )
            .select_from(Products)
            .join(ProductLinks, ProductLinks.product_id == Products.id)
            .join(PriceHistory, PriceHistory.link_id == ProductLinks.id)
            .join(Subscriptions, Subscriptions.product_id == Products.id)
            .where(Subscriptions.user_id == user_id)
            .group_by(Products.id)
        )
        result = await self.db.execute(query)
        prices = [float(row.max_price or 0) for row in result.all() if row.max_price]
        
        if not prices:
            return []
        
        max_price = max(prices)
        bucket_size = 5000
        if max_price > 50000:
            bucket_size = 10000
        if max_price > 100000:
            bucket_size = 25000
        if max_price > 250000:
            bucket_size = 50000
        
        buckets = {}
        for price in prices:
            bucket_start = int(price // bucket_size) * bucket_size
            bucket_end = bucket_start + bucket_size
            label = f"{bucket_start // 1000}к-{bucket_end // 1000}к"
            if bucket_start not in buckets:
                buckets[bucket_start] = {"range_min": bucket_start, "range_max": bucket_end, "count": 0, "label": label}
            buckets[bucket_start]["count"] += 1
        
        return sorted(buckets.values(), key=lambda x: x["range_min"])

    async def get_changes_timeline(self, user_id: int, days: int, limit: int = 50) -> list[dict]:
        """Получить timeline изменений цен (первая цена vs последняя за период)."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        price_range_subquery = (
            select(
                PriceHistory.link_id,
                func.min(PriceHistory.parsed_at).label("first_date"),
                func.max(PriceHistory.parsed_at).label("last_date"),
                func.min(PriceHistory.price).label("first_price"),
                func.max(PriceHistory.price).label("last_price")
            )
            .where(PriceHistory.parsed_at >= since_date)
            .group_by(PriceHistory.link_id)
            .subquery()
        )
        
        query = (
            select(
                func.date(price_range_subquery.c.last_date).label("date"),
                Products.id.label("product_id"),
                Products.title,
                price_range_subquery.c.first_price,
                price_range_subquery.c.last_price
            )
            .select_from(Products)
            .join(ProductLinks, ProductLinks.product_id == Products.id)
            .join(price_range_subquery, price_range_subquery.c.link_id == ProductLinks.id)
            .join(Subscriptions, Subscriptions.product_id == Products.id)
            .where(Subscriptions.user_id == user_id)
            .order_by(desc("date"))
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        events = []
        for row in rows:
            first_price = float(row.first_price)
            last_price = float(row.last_price)
            
            if first_price > 0 and first_price != last_price:
                change_percent = ((last_price - first_price) / first_price) * 100
                events.append({
                    "date": str(row.date),
                    "product_id": encode_id(row.product_id),
                    "title": row.title,
                    "price_from": first_price,
                    "price_to": last_price,
                    "change_percent": float(change_percent),
                    "is_drop": last_price < first_price
                })
        
        events.sort(key=lambda x: x["date"], reverse=True)
        return events[:limit]
