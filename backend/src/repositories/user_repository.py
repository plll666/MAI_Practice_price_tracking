from typing import Optional
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Users, Contacts
from src.schemas.auth import UserCreate, ContactCreate
from src.core.security import get_password_hash
from src.core.logger import logger


class UserRepository:
    """
    Репозиторий для выполнения операций с пользователями в базе данных.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_login(self, login: str) -> Optional[Users]:
        """
        Получает пользователя по логину.

        Args:
            login (str): Уникальный логин пользователя.

        Returns:
            Optional[Users]: Экземпляр модели Users, если найден, иначе None.

        Raises:
            SQLAlchemyError: При возникновении ошибки базы данных.
        """
        try:
            query = select(Users).where(Users.login == login)
            result = await self.db.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД в get_user_by_login: {e}")
            raise e

    async def create_user(self, user: UserCreate) -> Optional[Users]:
        """
        Создает нового пользователя в базе данных.

        Хеширует пароль перед сохранением.

        Args:
            user (UserCreate): Pydantic-схема с данными для регистрации.

        Returns:
            Optional[Users]: Созданный экземпляр модели Users.

        Raises:
            SQLAlchemyError: При ошибке записи в БД (например, нарушение ограничений).
        """
        try:
            hashed_password = get_password_hash(user.password)

            db_user = Users(
                login=user.login,
                password_hash=hashed_password,
                is_active=True
            )

            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Ошибка БД в create_user: {e}")
            raise e

    async def upsert_contacts(self, user_id: int, contacts_data: ContactCreate) -> Optional[Contacts]:
        """
        Создает или обновляет контактные данные для указанного пользователя.

        Этот метод реализует логику "update or insert":
        1. Ищет существующую запись контактов по `user_id`.
        2. Если запись не найдена, создает новую.
        3. Если запись найдена, обновляет в ней только те поля, которые
           были явно переданы в `contacts_data`.

        Args:
            user_id: ID пользователя, для которого обновляются контакты.
            contacts_data: Pydantic-схема с данными для обновления.

        Returns:
            Объект модели SQLAlchemy `Contacts` с актуальными данными.

        Raises:
            SQLAlchemyError: При возникновении ошибки взаимодействия с базой данных.
        """
        try:
            query = select(Contacts).where(Contacts.user_id == user_id)
            result = await self.db.execute(query)
            db_contacts = result.scalars().first()

            if not db_contacts:
                # Если контактов нет - создаем новый объект и привязываем к пользователю
                db_contacts = Contacts(user_id=user_id)
                self.db.add(db_contacts)

            # Получаем словарь только с теми полями, что прислал пользователь
            update_data = contacts_data.model_dump(exclude_unset=True)

            # Динамически обновляем атрибуты модели
            for key, value in update_data.items():
                setattr(db_contacts, key, value)

            await self.db.commit()
            await self.db.refresh(db_contacts)
            return db_contacts
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error in upsert_contacts: {e}")
            raise e