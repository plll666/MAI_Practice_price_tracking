import os
import requests
from typing import Optional
from src.core.logger import logger


class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.enabled = bool(self.bot_token)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None

        logger.info(f"TelegramService: enabled={self.enabled}")

    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """Отправить сообщение в Telegram."""
        if not self.enabled:
            logger.warning(f"Telegram not configured, skipping message to {chat_id}")
            return False

        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Telegram message sent to {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
            return False

    def send_price_alert(
        self,
        chat_id: str,
        product_title: str,
        product_url: str,
        current_price: float,
        target_price: float
    ) -> bool:
        """Отправить уведомление о снижении цены."""
        savings = target_price - current_price

        message = (
            f"🎉 <b>Цена снизилась!</b>\n\n"
            f"Товар: <b>{product_title}</b>\n"
            f"Было: <s>{target_price:.0f}₽</s>\n"
            f"Стало: <b>{current_price:.0f}₽</b>\n"
            f"Экономия: {savings:.0f}₽\n\n"
            f"<a href=\"{product_url}\">Посмотреть товар</a>"
        )

        return self.send_message(chat_id, message)

    def send_product_appeared(
        self,
        chat_id: str,
        product_title: str,
        product_url: str,
        current_price: float
    ) -> bool:
        """Отправить уведомление о появлении товара."""

        message = (
            f"🛒 <b>Товар появился в наличии!</b>\n\n"
            f"Товар: <b>{product_title}</b>\n"
            f"Цена: <b>{current_price:.0f}₽</b>\n\n"
            f"<a href=\"{product_url}\">Купить сейчас</a>"
        )

        return self.send_message(chat_id, message)

    def set_webhook(self, url: str) -> bool:
        """Установить вебхук."""
        if not self.enabled:
            logger.warning("Telegram not configured, cannot set webhook")
            return False

        try:
            webhook_url = f"{self.api_url}/setWebhook"
            payload = {"url": url}
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Webhook set to {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return False

    def delete_webhook(self) -> bool:
        """Удалить вебхук."""
        if not self.enabled:
            return False

        try:
            url = f"{self.api_url}/deleteWebhook"
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return False

    def get_webhook_info(self) -> Optional[dict]:
        """Получить информацию о вебхуке."""
        if not self.enabled:
            return None

        try:
            url = f"{self.api_url}/getWebhookInfo"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get webhook info: {e}")
            return None
