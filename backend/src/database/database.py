import os
import json
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
sql_echo = os.getenv("SQL_ECHO", "false").lower() == "true"

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_async_engine(
    DATABASE_URL, 
    echo=sql_echo,
    json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False)
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async_session = AsyncSessionLocal

sync_engine = create_engine(SYNC_DATABASE_URL, echo=sql_echo)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

async def get_db():
    """
        Зависимость, предоставляющая асинхронную сессию с базой данных.

        Результат:

        AsyncSession: сессия SQLAlchemy для взаимодействия с базой данных.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()