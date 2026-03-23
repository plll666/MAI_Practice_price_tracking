from typing import Optional
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Users
from src.schemas.auth import UserCreate
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