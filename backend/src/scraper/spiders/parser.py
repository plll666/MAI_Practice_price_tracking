import scrapy
import json
import re
from urllib.parse import urlsplit
from playwright_stealth import Stealth
from scraper.model import ParsedProduct
from dataclasses import replace

class ProbeSpider(scrapy.Spider):
    name = "parserpice"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not url:
            raise ValueError("url is required")
        self.start_url = url
        self.stealth_config = Stealth(
            navigator_languages_override=("ru-RU", "ru", "en-US", "en"),
            webgl_vendor_override="Intel Inc.",
            webgl_renderer_override="Intel Iris OpenGL Engine",
        )

    async def start(self):
        yield scrapy.Request(
            self.start_url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_init_callback": self.init_page,
                "playwright_page_goto_kwargs": {
                    "timeout": 30000,
                    "wait_until": "networkidle",
                }
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            },
            callback=self.parse,
            errback=self.handle_error
        )

    async def init_page(self, page, request):
        bad_stuff = re.compile(
            r"\.(woff|woff2|ttf|otf)$|tracker|analytics|top-fwz1|google|jivosite|kaspersky-labs")
        await page.route(bad_stuff, lambda route: route.abort())
        await self.stealth_config.apply_stealth_async(page)

        await page.set_extra_http_headers({
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {repr(failure)}")

    async def parse(self, response):
        page = response.meta["playwright_page"]

        try:
            try:
                await page.wait_for_selector('div[class*="ProductHeaderContentWrapper--StyledProductHeaderContentWrapper"]', timeout=5000)
                await page.wait_for_timeout(300)
            except Exception:
                self.logger.warning("Селектор не успел появиться, пробуем парсить как есть...")

            item = await self.parse_json_ld(response)

            if item:
                yield item
            else:
                self.logger.warning(f"No product data found for {response.url}")
                raise Exception("No product data found")

        except Exception as e:
            self.logger.error(f"Parse error for {response.url}: {e}")
            raise e
        finally:
            await page.close()

    async def parse_json_ld(self, response) -> ParsedProduct | None:
        """Парсинг JSON-LD разметки через от Playwright"""
        content = await response.meta["playwright_page"].content()
        return self.extract_json_ld_from_html(content, response.url)

    def extract_json_ld_from_html(self, html_content: str, url: str) -> ParsedProduct | None:
        """Извлечение JSON-LD из HTML-строки"""
        scripts = re.findall(
            r'<script [^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', 
            html_content,
            re.DOTALL
        )

        if not scripts:
            sel = scrapy.Selector(text=html_content)
            scripts = sel.xpath('//script[@type="application/ld+json"]/text()').getall()

        for raw in scripts:
            raw_clean = raw.strip()
            if not raw_clean or '"Product"' not in raw_clean:
                continue

            try:
                data = json.loads(raw_clean)
                objs = data if isinstance(data, list) else [data]

                for obj in objs:
                    if isinstance(obj, dict) and obj.get('@type') == 'Product':
                        product = self.extract_product_from_json_ld(obj, url)
                        
                        if product and "citilink.ru" in urlsplit(url).netloc:
                            sel = scrapy.Selector(text=html_content)
                            citilink_large_img = None                            
                            target_zone = sel.css('div[class*="ProductHeaderContentWrapper--StyledProductHeaderContentWrapper"]')
    
                            if target_zone:
                                for img_el in target_zone.css('img'):
                                    src = img_el.css('::attr(src)').get() or img_el.css('::attr(data-src)').get()
                                    if not src:
                                        continue                                        
                                    if 'width:55' in src or 'preview' in src.lower() or src.startswith('data:'):
                                        continue                                        
                                    citilink_large_img = src
                                    break

                            if citilink_large_img:
                                if citilink_large_img.startswith('//'):
                                    citilink_large_img = 'https:' + citilink_large_img
                                product = replace(product, image_url=citilink_large_img)                        
                                
                        return product
            except json.JSONDecodeError:
                continue

        return None

    def extract_product_from_json_ld(self, obj: dict, url: str) -> ParsedProduct:
        """Извлечение базовых полей продукта из структуры JSON-LD."""
        offers = obj.get('offers', {})
        if isinstance(offers, list) and offers:
            offers = offers[0]

        price_val = offers.get('price', 0) if offers else 0
        clean_price = int(re.sub(r'[^\d]', '', str(price_val))) if price_val else 0

        img_data = obj.get('image', [])
        img_url = ""
        if isinstance(img_data, list) and img_data:
            first = img_data[0]
            img_url = first.get('url') if isinstance(first, dict) else first
        elif isinstance(img_data, dict):
            img_url = img_data.get('url')
        else:
            img_url = str(img_data)

        if img_url.startswith('//'):
            img_url = 'https:' + img_url

        brand_info = obj.get('brand', {})
        brand = brand_info.get('name') if isinstance(brand_info, dict) else brand_info

        return ParsedProduct(
            title=str(obj.get('name', '')).strip(),
            price=clean_price,
            source=urlsplit(url).netloc,
            brand=brand,
            url=url,
            sku=str(obj.get('sku') or obj.get('mpn') or ""),
            image_url=img_url,
            properties=obj
        )
