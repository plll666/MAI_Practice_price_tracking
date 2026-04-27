from typing import Any

from src.celery.app import celery_app
from src.core.logger import logger
from src.repositories.celery_sync_repository import CelerySyncRepository
from src.services.email_service import EmailService


@celery_app.task(bind=True, name="src.celery.tasks.check_price_alerts")
def check_price_alerts_task(self) -> dict[str, Any]:
    logger.info("Checking for price alerts")
    
    repo = CelerySyncRepository()
    email_service = EmailService()
    
    try:
        subscriptions = repo.get_subscriptions_with_target_price()
        created_alerts = []
        
        for sub in subscriptions:
            current_price = repo.get_current_price_for_product(sub["product_id"])
            
            if current_price and current_price <= sub["target_price"]:
                if not repo.alert_exists_today(sub["user_id"], sub["product_id"]):
                    product_title = repo.get_product_title(sub["product_id"])
                    product_image = repo.get_product_image(sub["product_id"])
                    product_url = repo.get_product_url(sub["product_id"])

                    savings = sub["target_price"] - current_price
                    message = (
                        f"Цена на \"{product_title}\" снизилась до {current_price:.0f}₽! "
                        f"Вы сэкономите {savings:.0f}₽ (цель: {sub['target_price']:.0f}₽)"
                    )

                    alert_id = repo.create_alert(
                        user_id=sub["user_id"],
                        product_id=sub["product_id"],
                        message=message,
                        current_price=current_price,
                        target_price=sub["target_price"]
                    )

                    if alert_id > 0:
                        created_alerts.append({
                            "id": alert_id,
                            "user_id": sub["user_id"],
                            "product_id": sub["product_id"],
                            "current_price": current_price,
                            "target_price": sub["target_price"]
                        })

                        user_email = repo.get_user_email(sub["user_id"])
                        if user_email and product_url:
                            email_service.send_price_alert_email(
                                to=user_email,
                                product_title=product_title,
                                product_url=product_url,
                                current_price=current_price,
                                target_price=sub["target_price"],
                                image_url=product_image
                            )

                        logger.info(f"Создан алерт для товара {product_title}: {current_price}₽")

        logger.info(f"Создано {len(created_alerts)} алертов")
        return {"status": "success", "alerts": created_alerts}
    except Exception as e:
        logger.error(f"Error in check_price_alerts_task: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(bind=True, name="src.celery.tasks.check_price_appeared")
def check_price_appeared_task(self) -> dict[str, Any]:
    """Проверить появление товаров в наличии (цена была 0, стала > 0)."""
    logger.info("Checking for price appeared alerts")
    
    repo = CelerySyncRepository()
    email_service = EmailService()
    
    try:
        created_alerts = []
        all_subscriptions = repo.get_subscriptions_with_target_price()
        
        processed_products = set()
        
        for sub in all_subscriptions:
            product_id = sub["product_id"]
            
            if product_id in processed_products:
                continue
            
            current_price = repo.get_current_price_for_product(product_id)
            previous_price = repo.get_previous_price_for_product(product_id)
            
            if current_price and current_price > 0 and previous_price == 0:
                if not repo.alert_appeared_exists_today(sub["user_id"], product_id):
                    product_title = repo.get_product_title(product_id)
                    product_image = repo.get_product_image(product_id)
                    product_url = repo.get_product_url(product_id)

                    message = f"Товар \"{product_title}\" снова появился в наличии! Цена: {current_price:.0f}₽"

                    alert_id = repo.create_alert(
                        user_id=sub["user_id"],
                        product_id=product_id,
                        message=message,
                        current_price=current_price,
                        target_price=None
                    )

                    if alert_id > 0:
                        created_alerts.append({
                            "id": alert_id,
                            "user_id": sub["user_id"],
                            "product_id": product_id,
                            "current_price": current_price
                        })

                        user_email = repo.get_user_email(sub["user_id"])
                        if user_email and product_url:
                            email_service.send_product_appeared_email(
                                to=user_email,
                                product_title=product_title,
                                product_url=product_url,
                                current_price=current_price,
                                image_url=product_image
                            )

                        logger.info(f"Создан алерт о появлении товара {product_title}: {current_price}₽")
            
            processed_products.add(product_id)

        logger.info(f"Создано {len(created_alerts)} алертов о появлении товаров")
        return {"status": "success", "alerts": created_alerts}
    except Exception as e:
        logger.error(f"Error in check_price_appeared_task: {str(e)}")
        return {"status": "error", "error": str(e)}
