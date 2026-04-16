from typing import Optional
from src.repositories.price_history_repository import PriceHistoryRepository
from src.core.logger import logger


class PriceService:
    def __init__(self, repo: PriceHistoryRepository):
        self.repo = repo

    async def get_user_products_with_prices(self, user_id: int) -> list[dict]:
        """Получить товары пользователя с ценами."""
        return await self.repo.get_user_products_with_prices(user_id)

    async def get_product_price_history(
        self, 
        product_id: int, 
        days: int = 30
    ) -> dict:
        """Получить историю цен товара."""
        return await self.repo.get_product_price_history(product_id, days)

    async def get_current_price(self, product_id: int) -> Optional[float]:
        """Получить текущую цену."""
        return await self.repo.get_current_price(product_id)
