import pytest
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.database.models import Base, Users
from src.database import database as db_module
from src.core.security import get_password_hash
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from src.main import app

postgres = PostgresContainer("postgres:15-alpine")

@pytest_asyncio.fixture(scope="session", autouse=True)
def setup_postgres():
    postgres.start()
    url = postgres.get_connection_url().replace("postgresql+psycopg2", "postgresql+asyncpg")
    yield url
    postgres.stop()

@pytest_asyncio.fixture(scope="function")
async def test_db(setup_postgres):
    engine = create_async_engine(setup_postgres, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_db):
    factory = async_sessionmaker(test_db, expire_on_commit=False)
    async with factory() as session:
        yield session

@pytest_asyncio.fixture
async def test_user(db_session):
    async def _create_user(login="testuser", password="testpass123"):
        truncated_password = password[:72]
        user = Users(login=login, password_hash=get_password_hash(truncated_password), is_active=True)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
    return _create_user

@pytest_asyncio.fixture
async def client(test_db):
    factory = async_sessionmaker(test_db, expire_on_commit=False)
    
    async def override_get_db():
        async with factory() as session:
            yield session
    
    app.dependency_overrides[db_module.get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def sync_client():
    return TestClient(app)