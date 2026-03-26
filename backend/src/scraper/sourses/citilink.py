import asyncio
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from scrapy import Selector
from src.scraper.model import ParsedProduct

class CitilinkScraper:
    def __init__(self):
        self.source_name = "Citilink"

    async def scrape(self, url: str) -> ParsedProduct:
        async with Stealth().use_async(async_playwright()) as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_selector('h1', timeout=20000)
                await asyncio.sleep(random.uniform(2, 4))
                content = await page.content()
                sel = Selector(text=content)
                title = sel.css('h1::text').get()
                price_raw = (
                    sel.css('[data-testid="product-card-price-current"]::text').get() or 
                    sel.xpath("//span[contains(@class, 'MainPriceNumber')]/text()").get()
                )
                if not title or not price_raw:
                    raise ValueError(f"Не удалось получить данные с Ситилинка: {url}")
                price_int = int("".join(filter(str.isdigit, price_raw.replace('\xa0', ''))))
                return ParsedProduct(
                    title=title.strip(),
                    price=price_int,
                    source=self.source_name,
                    url=url
                )
            finally:
                await browser.close()