from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Products, ProductLinks, Shops, PriceHistory
from src.core.logger import logger
from urllib.parse import urlparse

class ProductRepository:
    """Репа для продуктов"""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_shop_id_by_url(self, url: str) -> int:
        """Возвращает магазин по ссылке через домен"""
        domain = urlparse(url).netloc.replace("www.", "")
        query = select(Shops.id).where(Shops.domain.contains(domain))
        result = await self.db.execute(query)
        shop_id = result.scalar_one_or_none()
        return shop_id if shop_id else 1

    async def get_or_create_product_by_url(self, url: str) -> Products:
        """Возвращает пролукт по url если такого url в базе нет создает новый продукт"""
        try:
            query = (
                select(ProductLinks)
                .options(joinedload(ProductLinks.product))
                .where(ProductLinks.url == url)
            )
            result = await self.db.execute(query)
            link = result.scalars().first()
            if link:
                logger.info(f"Продукт найден в базе: {link.product.id}")
                return link.product
            shop_id = await self._get_shop_id_by_url(url)
            new_product = Products(
                title="Pending parsing...",
                brand=None,
                properties={},
                image_url=None
            )
            self.db.add(new_product)
            await self.db.flush() 
            new_link = ProductLinks(
                url=url,
                product_id=new_product.id,
                shop_id=shop_id,
                is_available=True
            )
            self.db.add(new_link)
            await self.db.commit()
            await self.db.refresh(new_product)
            return new_product
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def update_product_details(self, product_id: int, url: str, title: str, price: float):
            """Обновляет название продукта и записывает цену в историю"""
            try:
                await self.db.execute(
                    update(Products).where(Products.id == product_id).values(title=title)
                )
                link_query = select(ProductLinks.id).where(
                    ProductLinks.product_id == product_id, 
                    ProductLinks.url == url
                )
                link_result = await self.db.execute(link_query)
                link_id = link_result.scalar_one_or_none()
                if link_id:
                    new_history = PriceHistory(
                        link_id=link_id,
                        price=price
                    )
                    self.db.add(new_history)
                await self.db.commit()                
                query = select(Products).where(Products.id == product_id)
                res = await self.db.execute(query)
                return res.scalar_one_or_none()
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Ошибка при сохранении данных парсинга: {e}")
                raise e