import scrapy
import json
import re
from urllib.parse import urlsplit
from playwright_stealth import Stealth
from scraper.model import ParsedProduct


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

    def start_requests(self):
        yield scrapy.Request(
            self.start_url, 
            meta={
                "playwright": True, 
                "playwright_include_page": True,
                "playwright_page_init_callback": self.init_page,
                "playwright_page_goto_kwargs": {
                    "timeout": 60000,
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
        bad_stuff = re.compile(r"\.(jpg|jpeg|png|gif|svg|webp|woff|woff2|ttf|otf|ico)$|tracker|analytics|top-fwz1|google|jivosite")
        await page.route(bad_stuff, lambda route: route.abort())
        await self.stealth_config.apply_stealth_async(page)
        
        await page.setExtraHTTPHeaders({
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {repr(failure)}")

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        try:
            await page.wait_for_timeout(2000)
            
            item = await self.parse_json_ld(response)
            if not item:
                item = await self.parse_html_fallback(page, response)
            
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
        """Парсинг JSON-LD разметки."""
        content = await response.meta["playwright_page"].content()
        
        scripts = re.findall(r'<script [^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', content, re.DOTALL)
        
        if not scripts:
            sel = scrapy.Selector(text=content)
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
                        return self.extract_product_from_json_ld(obj, response.url)
            except json.JSONDecodeError:
                continue
        
        return None

    def extract_product_from_json_ld(self, obj: dict, url: str) -> ParsedProduct:
        """Извлечение данных продукта из JSON-LD."""
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

    async def parse_html_fallback(self, page, response) -> ParsedProduct | None:
        """Fallback парсинг из HTML если JSON-LD не найден."""
        
        price_selectors = [
            'meta[property="product:price:amount"]::attr(content)',
            'meta[property="og:price:amount"]::attr(content)',
            '[data-price]::attr(data-price)',
            '.price-current::text',
            '.product-price::text',
            '.price__current::text',
            '.actual-price::text',
            '[class*="price"] [class*="current"]::text',
            '[class*="Price"]::text',
            '.product__price::text',
            '#priceblock_ourprice::text',
            '#priceblock_dealprice::text',
            '.a-price .a-offscreen::text',
            '[data-testid="price"]::text',
            '.price-value::text',
            '.special-price .price::text',
            '.regular-price .price::text',
        ]
        
        price = 0
        for selector in price_selectors:
            try:
                price_elem = await page.query_selector(selector)
                if price_elem:
                    price_text = await price_elem.text_content()
                    price_match = re.search(r'[\d\s]+', price_text or '')
                    if price_match:
                        clean = re.sub(r'[^\d]', '', price_match.group())
                        if clean:
                            price = int(clean)
                            break
            except Exception:
                continue
        
        if not price:
            try:
                price_elem = await page.query_selector('[class*="price"], .Price, #price, .price')
                if price_elem:
                    price_text = await price_elem.text_content()
                    price_match = re.search(r'[\d]+', price_text or '')
                    if price_match:
                        price = int(price_match.group())
            except Exception:
                pass

        title_selectors = [
            'meta[property="og:title"]::attr(content)',
            'meta[name="title"]::attr(content)',
            'h1[class*="title"]::text',
            '.product-title::text',
            '.product__title::text',
            'h1::text',
            '[data-testid="product-title"]::text',
        ]
        
        title = ""
        for selector in title_selectors:
            try:
                title_elem = await page.query_selector(selector)
                if title_elem:
                    title = (await title_elem.text_content()) or ""
                    title = title.strip()
                    if title and len(title) > 3:
                        break
            except Exception:
                continue
        
        if not title:
            try:
                h1 = await page.query_selector('h1')
                if h1:
                    title = (await h1.text_content()) or ""
                    title = title.strip()
            except Exception:
                pass

        image_selectors = [
            'meta[property="og:image"]::attr(content)',
            '[data-testid="product-image"] img::attr(src)',
            '.product-image img::attr(src)',
            '.product__image img::attr(src)',
            '[class*="gallery"] img::attr(src)',
            '[class*="carousel"] img::attr(src)',
            '#main-image::attr(src)',
            '.main-image img::attr(src)',
        ]
        
        image_url = ""
        for selector in image_selectors:
            try:
                img_elem = await page.query_selector(selector)
                if img_elem:
                    image_url = await img_elem.get_attribute('src') or ""
                    if image_url and len(image_url) > 10:
                        break
            except Exception:
                continue
        
        if image_url.startswith('//'):
            image_url = 'https:' + image_url

        if not title and not price:
            self.logger.warning(f"Fallback parsing failed for {response.url}")
            return None

        return ParsedProduct(
            title=title or "Unknown Product",
            price=price,
            source=urlsplit(response.url).netloc,
            brand="",
            url=response.url,
            sku="",
            image_url=image_url,
            properties={}
        )
