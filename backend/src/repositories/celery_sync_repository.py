from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, update

from src.database.database import SyncSessionLocal
from src.database.models import ProductLinks, PriceHistory, Subscriptions, Users, Products, Alerts, Contacts


class CelerySyncRepository:
    """Репозиторий для Celery задач (синхронный)."""

    def get_all_active_links(self) -> list[tuple[int, str]]:
        """Получить все активные ссылки для парсинга."""
        db = SyncSessionLocal()
        try:
            query = (
                select(ProductLinks.id, ProductLinks.url)
                .where(ProductLinks.is_available == True)
            )
            result = db.execute(query)
            return list(result.all())
        finally:
            db.close()

    def get_user_links(self, user_id: int) -> list[tuple[int, str]]:
        """Получить ссылки пользователя."""
        db = SyncSessionLocal()
        try:
            query = (
                select(ProductLinks.id, ProductLinks.url)
                .join(Subscriptions, Subscriptions.product_id == ProductLinks.product_id)
                .where(Subscriptions.user_id == user_id)
            )
            result = db.execute(query)
            return list(result.all())
        finally:
            db.close()

    def get_users_need_parsing(self, interval_seconds: int) -> list[int]:
        """Получить пользователей, которым нужен парсинг."""
        db = SyncSessionLocal()
        try:
            now = datetime.utcnow()
            query = select(Users).where(Users.is_active == True)
            result = db.execute(query)
            users = result.scalars().all()

            user_ids = []
            for user in users:
                user_interval = user.parse_interval or interval_seconds
                if not user.last_parse_at:
                    user_ids.append(user.id)
                elif (now - user.last_parse_at).total_seconds() >= user_interval:
                    user_ids.append(user.id)

            return user_ids
        finally:
            db.close()

    def update_last_parse_at(self, user_id: int) -> None:
        """Обновить время последнего парсинга."""
        db = SyncSessionLocal()
        try:
            db.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(last_parse_at=datetime.utcnow())
            )
            db.commit()
        finally:
            db.close()

    def add_price_record(self, link_id: int, price: float) -> bool:
        """Добавить запись о цене."""
        db = SyncSessionLocal()
        try:
            new_record = PriceHistory(link_id=link_id, price=price)
            db.add(new_record)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

    def get_subscriptions_with_target_price(self) -> list[dict]:
        """Получить подписки с целевой ценой."""
        db = SyncSessionLocal()
        try:
            query = (
                select(
                    Subscriptions.id,
                    Subscriptions.user_id,
                    Subscriptions.product_id,
                    Subscriptions.target_price,
                    Subscriptions.notified_at
                )
                .where(Subscriptions.target_price.isnot(None))
            )
            result = db.execute(query)
            rows = result.all()
            return [
                {
                    "id": row.id,
                    "user_id": row.user_id,
                    "product_id": row.product_id,
                    "target_price": float(row.target_price),
                    "notified_at": row.notified_at
                }
                for row in rows
            ]
        finally:
            db.close()

    def set_subscription_notified(self, subscription_id: int) -> None:
        """Установить время уведомления для подписки."""
        db = SyncSessionLocal()
        try:
            db.execute(
                update(Subscriptions)
                .where(Subscriptions.id == subscription_id)
                .values(notified_at=datetime.utcnow())
            )
            db.commit()
        finally:
            db.close()

    def reset_subscription_notified(self, subscription_id: int) -> None:
        """Сбросить время уведомления (когда цена поднялась выше цели)."""
        db = SyncSessionLocal()
        try:
            db.execute(
                update(Subscriptions)
                .where(Subscriptions.id == subscription_id)
                .values(notified_at=None)
            )
            db.commit()
        finally:
            db.close()

    def get_current_price_for_product(self, product_id: int) -> Optional[float]:
        """Получить текущую цену товара."""
        db = SyncSessionLocal()
        try:
            query = (
                select(PriceHistory.price)
                .join(ProductLinks, ProductLinks.id == PriceHistory.link_id)
                .where(ProductLinks.product_id == product_id)
                .order_by(PriceHistory.parsed_at.desc())
                .limit(1)
            )
            result = db.execute(query)
            price = result.scalar_one_or_none()
            return float(price) if price else None
        finally:
            db.close()

    def get_product_title(self, product_id: int) -> str:
        """Получить название товара."""
        db = SyncSessionLocal()
        try:
            query = select(Products.title).where(Products.id == product_id)
            result = db.execute(query)
            title = result.scalar_one_or_none()
            return title or "Товар"
        finally:
            db.close()

    def get_product_image(self, product_id: int) -> Optional[str]:
        """Получить изображение товара."""
        db = SyncSessionLocal()
        try:
            query = select(Products.image_url).where(Products.id == product_id)
            result = db.execute(query)
            return result.scalar_one_or_none()
        finally:
            db.close()

    def alert_exists_today(self, user_id: int, product_id: int) -> bool:
        """Проверить, существует ли алерт для товара сегодня."""
        db = SyncSessionLocal()
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            query = (
                select(Alerts)
                .where(
                    Alerts.user_id == user_id,
                    Alerts.product_id == product_id,
                    Alerts.created_at >= today_start
                )
            )
            result = db.execute(query)
            return result.scalar_one_or_none() is not None
        finally:
            db.close()

    def create_alert(
        self,
        user_id: int,
        product_id: int,
        message: str,
        current_price: float,
        target_price: float = None
    ) -> int:
        """Создать алерт и вернуть его ID."""
        db = SyncSessionLocal()
        try:
            new_alert = Alerts(
                user_id=user_id,
                product_id=product_id,
                message=message,
                current_price=current_price,
                target_price=target_price,
                is_read=False
            )
            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)
            return new_alert.id
        except Exception:
            db.rollback()
            return 0
        finally:
            db.close()

    def get_previous_price_for_product(self, product_id: int) -> Optional[float]:
        """Получить предыдущую цену товара (до текущей)."""
        db = SyncSessionLocal()
        try:
            query = (
                select(PriceHistory.price)
                .join(ProductLinks, ProductLinks.id == PriceHistory.link_id)
                .where(ProductLinks.product_id == product_id)
                .order_by(PriceHistory.parsed_at.desc())
                .offset(1)
                .limit(1)
            )
            result = db.execute(query)
            price = result.scalar_one_or_none()
            return float(price) if price else None
        finally:
            db.close()

    def get_subscriptions_for_product(self, product_id: int) -> list[dict]:
        """Получить все подписки для товара."""
        db = SyncSessionLocal()
        try:
            query = (
                select(Subscriptions.user_id)
                .where(Subscriptions.product_id == product_id)
            )
            result = db.execute(query)
            return [{"user_id": row.user_id} for row in result.all()]
        finally:
            db.close()

    def alert_appeared_exists_today(self, user_id: int, product_id: int) -> bool:
        """Проверить, существует ли алерт о появлении товара сегодня."""
        db = SyncSessionLocal()
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            query = (
                select(Alerts)
                .where(
                    Alerts.user_id == user_id,
                    Alerts.product_id == product_id,
                    Alerts.created_at >= today_start,
                    Alerts.message.like('%появился%')
                )
            )
            result = db.execute(query)
            return result.scalar_one_or_none() is not None
        finally:
            db.close()

    def get_user_email(self, user_id: int) -> Optional[str]:
        """Получить email пользователя из контактов."""
        db = SyncSessionLocal()
        try:
            query = select(Contacts.email).where(Contacts.user_id == user_id)
            result = db.execute(query)
            return result.scalar_one_or_none()
        finally:
            db.close()

    def get_product_url(self, product_id: int) -> Optional[str]:
        """Получить первую ссылку товара."""
        db = SyncSessionLocal()
        try:
            query = (
                select(ProductLinks.url)
                .where(ProductLinks.product_id == product_id)
                .limit(1)
            )
            result = db.execute(query)
            return result.scalar_one_or_none()
        finally:
            db.close()
