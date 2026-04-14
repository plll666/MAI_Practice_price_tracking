from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Users


class SettingsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_parse_interval(self, user_id: int) -> int:
        result = await self.db.execute(
            select(Users.parse_interval).where(Users.id == user_id)
        )
        return result.scalar_one_or_none() or 1

    async def set_parse_interval(self, user_id: int, interval: int) -> None:
        await self.db.execute(
            update(Users).where(Users.id == user_id).values(parse_interval=interval)
        )
        await self.db.commit()