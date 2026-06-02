import pytest
from unittest.mock import MagicMock, AsyncMock
from src.services.product_service import ProductService
from src.schemas.products import ProductCreate
from src.celery_work.app import celery_app

@pytest.mark.asyncio
class TestProductServiceIntegration:
    
    async def test_add_and_parse_product_integration(self):
        mock_repo = MagicMock()
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.title = "Test Product"
        mock_repo.get_or_create_product_by_url = AsyncMock(return_value=mock_product)
        
        service = ProductService(mock_repo)
        product_data = ProductCreate(url="https://example.com/product", target_price=100.0)
        
        with pytest.raises(Exception):
            await service.add_and_parse_product(user_id=1, product_data=product_data)

    async def test_get_all_products_integration(self):
        mock_repo = MagicMock()
        mock_repo.get_all_products = AsyncMock(return_value=[])
        
        service = ProductService(mock_repo)
        result = await service.get_all_products(user_id=1)
        assert isinstance(result, list)

    async def test_get_product_by_id_integration(self):
        mock_repo = MagicMock()
        mock_repo.get_product_by_id = AsyncMock(return_value=None)
        
        service = ProductService(mock_repo)
        result = await service.get_product_by_id(1, user_id=1)
        assert result is None

    async def test_update_target_price_integration(self):
        mock_repo = MagicMock()
        mock_repo.update_target_price = AsyncMock(return_value=True)
        
        service = ProductService(mock_repo)
        result = await service.update_target_price(user_id=1, product_id=1, target_price=50.0)
        assert result == True