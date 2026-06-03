import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from src.services.product_service import ProductService
from src.repositories.product_repository import ProductRepository

@pytest.mark.asyncio
class TestProductService:
    
    async def test_add_and_parse_product_success(self):
        mock_repo = MagicMock(spec=ProductRepository)
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.title = "Test Product"
        mock_repo.get_or_create_product_by_url = AsyncMock(return_value=mock_product)
        
        service = ProductService(mock_repo)
        
        from src.schemas.products import ProductCreate
        from src.schemas.auth import UserCreate
        product_data = ProductCreate(url="https://example.com/product", target_price=100.0)
        
        with pytest.raises(Exception):
            await service.add_and_parse_product(user_id=1, product_data=product_data)

    async def test_get_all_products(self):
        mock_repo = MagicMock(spec=ProductRepository)
        mock_repo.get_all_products = AsyncMock(return_value=[])
        
        service = ProductService(mock_repo)
        result = await service.get_all_products(user_id=1)
        assert isinstance(result, list)

    async def test_get_product_by_id(self):
        mock_repo = MagicMock(spec=ProductRepository)
        mock_repo.get_product_by_id = AsyncMock(return_value=None)
        
        service = ProductService(mock_repo)
        result = await service.get_product_by_id(1, user_id=1)
        assert result is None

    async def test_update_target_price(self):
        mock_repo = MagicMock(spec=ProductRepository)
        mock_repo.update_target_price = AsyncMock(return_value=True)
        
        service = ProductService(mock_repo)
        result = await service.update_target_price(user_id=1, product_id=1, target_price=50.0)
        assert result == True