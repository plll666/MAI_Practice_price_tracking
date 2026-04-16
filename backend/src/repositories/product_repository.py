from sqlalchemy import select, update, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Products, ProductLinks, Shops, PriceHistory, Subscriptions
from src.core.logger import logger
from urllib.parse import urlparse
from typing import Optional

class ProductRepository:
    """Репа для продуктов"""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_shop_id_by_url(self, url: str) -> int:
        """Находит магазин по домену или создает новый, если его нет"""
        domain = urlparse(url).netloc.replace("www.", "")
        query = select(Shops.id).where(Shops.domain.contains(domain))
        result = await self.db.execute(query)
        shop_id = result.scalar_one_or_none()
        if shop_id:
            return shop_id
        try:
            shop_name = domain.split('.')[0].capitalize()
            new_shop = Shops(name=shop_name, domain=domain)
            self.db.add(new_shop)
            await self.db.flush() 
            logger.info(f"Автоматически создан магазин: {shop_name}")
            return new_shop.id
        except Exception as e:
            logger.error(f"Ошибка при создании магазина для {domain}: {e}")
            return 1
    async def get_or_create_product_by_url(self, user_id: int, url: str, title: str, brand: str, price: int, image_url: str, properties: dict = None, target_price: float = None) -> Products:
        """Возвращает продукт по url если такого url в базе нет создает новый продукт"""
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
                product = await self.update_product_details(link.product.id, url, title, price, brand, properties)
            else:
                shop_id = await self._get_shop_id_by_url(url)
   
                product = Products(
                    title=title,
                    brand=brand,
                    properties=properties or {},
                    image_url=image_url
                )
                self.db.add(product)
                await self.db.flush() 
                
                new_link = ProductLinks(
                    url=url,
                    product_id=product.id,
                    shop_id=shop_id,
                    is_available=True,
                )
                self.db.add(new_link)
                await self.db.flush()
                
                new_price = PriceHistory(
                    link_id=new_link.id,
                    price=price
                )

                self.db.add(new_price)
                await self.db.flush()
            sub_query = select(Subscriptions).where(
                Subscriptions.user_id == user_id, 
                Subscriptions.product_id == product.id
            )
            sub_result = await self.db.execute(sub_query)
            existing_sub = sub_result.scalar_one_or_none()
            if not existing_sub:
                final_target_price = target_price
                if target_price is None:
                    final_target_price = round(price * 0.8, 2)
                    logger.info(f"Автоматическая желаемая цена: {final_target_price} (80% от {price})")
                new_sub = Subscriptions(
                    user_id=user_id,
                    product_id=product.id,
                    target_price=final_target_price
                )
                self.db.add(new_sub)
            elif target_price is not None:
                existing_sub.target_price = target_price
            await self.db.commit()
            await self.db.refresh(product)
            return product
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Eror to create/update product: {e}")
            raise e

    async def update_product_details(self, product_id: int, url: str, title: str, price: float, brand: str = None, properties: dict = None) -> Products:
        """Обновляет информацию о продукте и добавляет новую запись цены"""
        try:
            update_data = {"title": title}
            if brand:
                update_data["brand"] = brand
            if properties:
                update_data["properties"] = properties
            await self.db.execute(
                update(Products)
                .where(Products.id == product_id)
                .values(**update_data)
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
            logger.error(f"ERROR: error with updating product: {product_id}: {e}")
            raise e
            
    async def get_all_products(self, user_id: int) -> list[Products]:
        """Теперь получает товары только того юзера, чей ID передали"""
        try:
            query = (
                select(Products)
                .join(Subscriptions)
                .where(Subscriptions.user_id == user_id)
                .order_by(Products.id.desc())
            )
            result = await self.db.execute(query)
            products = result.scalars().all()
            
            for product in products:
                price_query = (
                    select(PriceHistory.price)
                    .join(ProductLinks)
                    .where(ProductLinks.product_id == product.id)
                    .order_by(PriceHistory.parsed_at.desc())
                    .limit(1)
                )
                price_res = await self.db.execute(price_query)
                last_price = price_res.scalar_one_or_none()
                product.current_price = float(last_price) if last_price else 0.0
                
                url_query = (
                    select(ProductLinks.url)
                    .where(ProductLinks.product_id == product.id)
                    .limit(1)
                )
                url_res = await self.db.execute(url_query)
                product.url = url_res.scalar_one_or_none()
            return list(products)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении списка продуктов юзера {user_id}: {e}")
            return []

    async def get_product_by_id(self, product_id: int, user_id: int = None) -> Optional[Products]:
        try:
            query = (
                select(Products)
                .join(Subscriptions)
                .where(Products.id == product_id)
            )
            
            if user_id:
                query = query.where(Subscriptions.user_id == user_id)
            
            result = await self.db.execute(query)
            product = result.scalar_one_or_none()
            
            if product:
                price_query = (
                    select(PriceHistory.price)
                    .join(ProductLinks, ProductLinks.id == PriceHistory.link_id)
                    .where(ProductLinks.product_id == product_id)
                    .order_by(desc(PriceHistory.parsed_at))
                    .limit(1)
                )
                price_result = await self.db.execute(price_query)
                current_price = price_result.scalar_one_or_none()
                product.current_price = float(current_price) if current_price else 0.0
                
                target_query = (
                    select(Subscriptions.target_price)
                    .where(
                        Subscriptions.user_id == user_id,
                        Subscriptions.product_id == product_id
                    )
                )
                target_result = await self.db.execute(target_query)
                target_price = target_result.scalar_one_or_none()
                product.target_price = float(target_price) if target_price else None
                
                url_query = (
                    select(ProductLinks.url)
                    .where(ProductLinks.product_id == product_id)
                    .limit(1)
                )
                url_result = await self.db.execute(url_query)
                product.url = url_result.scalar_one_or_none()
            return product
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении продукта {product_id}: {e}")
            return None

    async def update_target_price(self, user_id: int, product_id: int, target_price: Optional[float]) -> bool:
        """Обновить желаемую цену в подписке пользователя."""
        try:
            query = (
                update(Subscriptions)
                .where(
                    Subscriptions.user_id == user_id,
                    Subscriptions.product_id == product_id
                )
                .values(target_price=target_price)
            )
            await self.db.execute(query)
            await self.db.commit()
            logger.info(f"Обновлен target_price для product_id={product_id}, user_id={user_id}: {target_price}")
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Ошибка обновления target_price: {e}")
            return False