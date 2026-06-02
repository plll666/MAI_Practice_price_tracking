import pytest
from src.schemas.products import TargetPriceUpdate, ProductResponse

class TestSchemas:
    
    def test_target_price_update_schema(self):
        schema = TargetPriceUpdate(target_price=50.0)
        assert schema.target_price == 50.0

    def test_product_response_schema(self):
        schema = ProductResponse(id="abc123", title="Test Product")
        assert schema.id == "abc123"
        assert schema.title == "Test Product"