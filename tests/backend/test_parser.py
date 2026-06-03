import os
import re
import json
import logging
import pytest
import scrapy
from unittest.mock import AsyncMock, MagicMock, patch
from twisted.python.failure import Failure
from scraper.spiders.parser import ProbeSpider  
from scraper.model import ParsedProduct

@pytest.fixture
def citilink_html():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(current_dir, "fixtures", "product_example.html")
    
    if not os.path.exists(fixture_path):
        pytest.fail(f"Fixture not found: {fixture_path}")
        
    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


def test_citilink_parsing_success(citilink_html):
    target_url = "https://www.citilink.ru/product/mysh-logitech-g502-hero-igrovaya-opticheskaya-provodnaya-usb-chernyi-9-1976552/"
    
    spider = ProbeSpider(url=target_url)
    product = spider.extract_json_ld_from_html(citilink_html, target_url)
    
    assert product is not None
    assert isinstance(product, ParsedProduct)
    assert isinstance(product.title, str) and len(product.title) > 0
    assert isinstance(product.price, int) and product.price > 0
    assert isinstance(product.brand, str) and len(product.brand) > 0
    assert len(product.sku) > 0
    assert product.source == "www.citilink.ru"
    assert product.url == target_url
    assert isinstance(product.image_url, str)
    assert product.image_url.startswith("http")
    assert "width:55" not in product.image_url

def test_parsing_returns_none_on_invalid_html():
    spider = ProbeSpider(url="https://www.citilink.ru/")
    invalid_html = "<html><body><h1>Page</h1></body></html>"
    
    product = spider.extract_json_ld_from_html(invalid_html, "https://www.citilink.ru/")
    assert product is None

def test_extract_json_ld_handling_broken_json_and_structures():
    spider = ProbeSpider(url="https://www.citilink.ru/")
    
    html = """
    <html>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Сломанный блок"
        </script>
        
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Игровая Мышь",
            "sku": "999111",
            "brand": {"@type": "Brand", "name": "Logitech"},
            "image": {
                "@type": "ImageObject",
                "url": "https://img.citilink.ru/item_main.jpg"
            },
            "offers": [
                {
                    "@type": "Offer",
                    "price": "3500",
                    "priceCurrency": "RUB"
                }
            ]
        }
        </script>
    </html>
    """
    product = spider.extract_json_ld_from_html(html, "https://www.citilink.ru/")
    
    assert product is not None
    assert product.title == "Игровая Мышь"
    assert product.price == 3500
    assert product.image_url == "https://img.citilink.ru/item_main.jpg"

def test_spider_requires_url():
    with pytest.raises(ValueError, match="url is required"):
        ProbeSpider(url="")

    with pytest.raises(ValueError, match="url is required"):
        ProbeSpider(url=None)

@pytest.mark.asyncio
async def test_start_requests_yields_playwright_request():
    target_url = "https://www.citilink.ru/product/some-item/"
    spider = ProbeSpider(url=target_url)
    
    requests = []
    async for req in spider.start():
        requests.append(req)
        
    assert len(requests) == 1
    req = requests[0]
    assert isinstance(req, scrapy.Request)
    assert req.url == target_url
    assert req.meta.get("playwright") is True
    assert req.meta.get("playwright_include_page") is True
    assert req.callback == spider.parse
    assert req.errback == spider.handle_error
    assert "User-Agent" in req.headers


@pytest.mark.asyncio
async def test_init_page_configuration():
    spider = ProbeSpider(url="https://www.citilink.ru/")
    spider.stealth_config = AsyncMock()
    
    mock_page = AsyncMock()
    mock_request = MagicMock()
    
    await spider.init_page(mock_page, mock_request)
    
    mock_page.route.assert_called_once()
    args, _ = mock_page.route.call_args
    assert isinstance(args[0], re.Pattern)
    
    spider.stealth_config.apply_stealth_async.assert_called_once_with(mock_page)
    mock_page.set_extra_http_headers.assert_called_once_with({
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    })

def test_handle_error_logging(caplog):
    spider = ProbeSpider(url="https://www.citilink.ru/")
    
    fake_exception = Exception("Proxy Connection Timeout")
    failure = Failure(fake_exception)
    
    # Используем caplog для перехвата логов любого уровня сложности
    with caplog.at_level(logging.ERROR):
        spider.handle_error(failure)
        
    assert any("Request failed" in record.message for record in caplog.records)

@pytest.mark.asyncio
async def test_parse_lifecycle_success():
    spider = ProbeSpider(url="https://www.citilink.ru/")
    
    mock_page = AsyncMock()
    mock_page.content.return_value = "<html><body>Успешно</body></html>"
    
    response = MagicMock(spec=scrapy.http.Response)
    response.url = "https://www.citilink.ru/product/item"
    response.meta = {"playwright_page": mock_page}
    
    mock_product = ParsedProduct(
        title="Тест", price=100, brand="B", sku="1", 
        source="citilink.ru", url=response.url, image_url="http://img"
    )
    spider.parse_json_ld = AsyncMock(return_value=mock_product)
    
    results = []
    async for item in spider.parse(response):
        results.append(item)
        
    assert len(results) == 1
    assert results[0] == mock_product
    mock_page.wait_for_selector.assert_called_once()
    mock_page.close.assert_called_once()

@pytest.mark.asyncio
async def test_parse_lifecycle_selector_timeout_and_fallback(caplog):
    """Покрывает: таймаут ожидания селектора, логгирование warning и ошибку пустого результата"""
    spider = ProbeSpider(url="https://www.citilink.ru/")
    
    mock_page = AsyncMock()
    mock_page.wait_for_selector.side_effect = Exception("Timeout")
    mock_page.content.return_value = "<html></html>"
    
    response = MagicMock(spec=scrapy.http.Response)
    response.url = "https://www.citilink.ru/product/item"
    response.meta = {"playwright_page": mock_page}
    
    spider.parse_json_ld = AsyncMock(return_value=None)
    
    with caplog.at_level(logging.WARNING):
        with pytest.raises(Exception, match="No product data found"):
            async for _ in spider.parse(response):
                pass
                
    messages = [record.message for record in caplog.records]
    assert any("Селектор не успел появиться, пробуем парсить как есть..." in msg for msg in messages)
    assert any("Parse error for" in msg for msg in messages)
            
    mock_page.close.assert_called_once()

@pytest.mark.asyncio
async def test_parse_json_ld_calls_extractor():
    spider = ProbeSpider(url="https://www.citilink.ru/")
    
    mock_page = AsyncMock()
    mock_page.content.return_value = "<html>Fake Content</html>"
    
    response = MagicMock(spec=scrapy.http.Response)
    response.url = "https://www.citilink.ru/target"
    response.meta = {"playwright_page": mock_page}
    
    spider.extract_json_ld_from_html = MagicMock(return_value=None)
    
    await spider.parse_json_ld(response)
    
    mock_page.content.assert_called_once()
    spider.extract_json_ld_from_html.assert_called_once_with("<html>Fake Content</html>", response.url)