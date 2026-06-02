import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.database.models import Products, ProductLinks, Subscriptions, PriceHistory
from src.repositories.product_repository import ProductRepository

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def test_db():
    from src.database.models import Base
    engine = create_async_engine(TEST_DB_URL, echo=False)
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

@pytest.mark.asyncio
class TestProductRepository:
    
    async def test_get_all_products(self, db_session):
        repo = ProductRepository(db_session)
        
        product = Products(title="Test", brand="Brand")
        db_session.add(product)
        await db_session.flush()
        
        link = ProductLinks(id=1, url="https://test.com", product_id=product.id)
        db_session.add(link)
        await db_session.flush()
        
        sub = Subscriptions(user_id=1, product_id=product.id, target_price=100.0)
        db_session.add(sub)
        await db_session.commit()
        
        products = await repo.get_all_products(user_id=1)
        assert len(products) == 1
        assert products[0].title == "Test"

    async def test_get_product_by_id(self, db_session):
        repo = ProductRepository(db_session)
        
        product = Products(title="Test", brand="Brand")
        db_session.add(product)
        await db_session.flush()
        
        link = ProductLinks(id=1, url="https://test.com", product_id=product.id)
        db_session.add(link)
        await db_session.flush()
        
        sub = Subscriptions(user_id=1, product_id=product.id, target_price=100.0)
        db_session.add(sub)
        await db_session.commit()
        
        result = await repo.get_product_by_id(product.id, user_id=1)
        assert result is not None
        assert result.title == "Test"

    async def test_update_target_price_success(self, db_session):
        repo = ProductRepository(db_session)
        
        product = Products(title="Test", brand="Brand")
        db_session.add(product)
        await db_session.flush()
        
        sub = Subscriptions(user_id=1, product_id=product.id, target_price=100.0)
        db_session.add(sub)
        await db_session.commit()
        
        result = await repo.update_target_price(user_id=1, product_id=product.id, target_price=50.0)
        assert result == True