import pytest
from src.scraper.protocol import BaseSpider
from src.scraper.model import ParsedProduct
from typing import Protocol, runtime_checkable

class TestBaseSpiderProtocol:
    
    def test_protocol_exists(self):
        assert BaseSpider is not None

    def test_protocol_is_runtime_checkable(self):
        assert runtime_checkable(BaseSpider)

    def test_protocol_has_scrape_method(self):
        assert hasattr(BaseSpider, 'scrape')