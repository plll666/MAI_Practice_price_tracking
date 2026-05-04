import string
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Users
from src.services.telegram_service import TelegramService
from src.core.logger import logger


class TelegramHandler:
    def __init__(self):
        self.telegram_service = TelegramService()

    async def process_update(self, update: dict, db: AsyncSession):
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()

        if not chat_id or not text:
            return

        if text == "/start":
            await self.handle_start(chat_id, db)
        elif text == "/unlink":
            await self.handle_unlink(chat_id, db)
        elif len(text) == 6 and text.isalnum():
            await self.handle_linking_code(chat_id, text, db)

    async def handle_start(self, chat_id: int, db: AsyncSession):
        result = await db.execute(select(Users).filter(Users.chat_id == str(chat_id)))
        user = result.scalar_one_or_none()

        if user:
            await self.telegram_service.send_message(
                chat_id=chat_id,
                text="✅ Ваш Telegram уже привязан к аккаунту!"
            )
            return

        await self.telegram_service.send_message(
            chat_id=chat_id,
            text=(
                "👋 Привет! Я бот уведомлений MAI Price Tracker.\n\n"
                "Для привязки аккаунта:\n"
                "1. Перейдите в настройки на сайте\n"
                "2. Нажмите 'Подключить Telegram'\n"
                "3. Введите код, который появится на сайте\n\n"
                "Команды:\n"
                "/start - показать это сообщение\n"
                "/unlink - отвязать Telegram от аккаунта"
            )
        )
        logger.info(f"User {chat_id} started bot, waiting for linking code")

    async def handle_linking_code(self, chat_id: int, code: str, db: AsyncSession):
        result = await db.execute(
            select(Users).filter(
                Users.telegram_linking_code == code,
                Users.telegram_linking_code_expires > datetime.utcnow()
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            await self.telegram_service.send_message(
                chat_id=chat_id,
                text="❌ Неверный или устаревший код. Получите новый код в настройках."
            )
            return

        user.chat_id = str(chat_id)
        user.telegram_linking_code = None
        user.telegram_linking_code_expires = None
        await db.commit()

        await self.telegram_service.send_message(
            chat_id=chat_id,
            text=(
                "✅ Telegram успешно подключен!\n\n"
                "Теперь вы будете получать уведомления о снижении цен."
            )
        )
        logger.info(f"Telegram linked: chat_id={chat_id} to user_id={user.id}")

    async def handle_unlink(self, chat_id: int, db: AsyncSession):
        result = await db.execute(select(Users).filter(Users.chat_id == str(chat_id)))
        user = result.scalar_one_or_none()

        if not user:
            await self.telegram_service.send_message(
                chat_id=chat_id,
                text="❌ Ваш Telegram не привязан к аккаунту."
            )
            return

        user.chat_id = None
        user.telegram_notifications_enabled = False
        user.telegram_linking_code = None
        user.telegram_linking_code_expires = None
        await db.commit()

        await self.telegram_service.send_message(
            chat_id=chat_id,
            text="✅ Telegram успешно отвязан от аккаунта."
        )
        logger.info(f"Telegram unlinked: chat_id={chat_id} from user_id={user.id}")
