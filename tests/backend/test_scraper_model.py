import pytest
from src.scraper.model import ParsedProduct

class TestParsedProduct:
    
    def test_create_parsed_product(self):
        product = ParsedProduct(
            title="Test Product",
            price=1000,
            source="example.com",
            brand="TestBrand",
            url="https://example.com/product",
            sku="12345"
        )
        assert product.title == "Test Product"
        assert product.price == 1000
        assert product.source == "example.com"

    def test_parsed_product_with_image_url(self):
        product = ParsedProduct(
            title="Test Product",
            price=1000,
            source="example.com",
            brand="TestBrand",
            url="https://example.com/product",
            sku="12345",
            image_url="https://example.com/image.jpg"
        )
        assert product.image_url == "https://example.com/image.jpg"

    def test_parsed_product_frozen(self):
        product = ParsedProduct(
            title="Test Product",
            price=1000,
            source="example.com",
            brand="TestBrand",
            url="https://example.com/product",
            sku="12345"
        )
        with pytest.raises(Exception):
            product.title = "Changed"