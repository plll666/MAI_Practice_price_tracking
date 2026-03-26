from typing import Protocol, runtime_checkable
from model import ParsedProduct

@runtime_checkable
class BaseSpider(Protocol):
    """База для пауков"""
    async def scrape(self, url:str) -> ParsedProduct:
        ...