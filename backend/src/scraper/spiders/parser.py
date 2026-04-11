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
        self.stealth_config = Stealth(navigator_languages_override=("ru-RU", "ru"))

    def start_requests(self):
        yield scrapy.Request(
            self.start_url, 
            meta={
                "playwright": True, 
                "playwright_include_page": True,
                "playwright_page_init_callback": self.init_page,
                "playwright_page_goto_kwargs": {
                    "timeout": 30000,
                    "wait_until": "domcontentloaded",
                }
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            },
            callback=self.parse,
            errback=self.handle_error
        )

    async def init_page(self, page, request):
        bad_stuff = re.compile(r"\.(jpg|jpeg|png|gif|svg|webp|woff|woff2|ttf|otf)$|tracker|analytics|top-fwz1")
        await page.route(bad_stuff, lambda route: route.abort())
        await self.stealth_config.apply_stealth_async(page)

    def handle_error(self, failure):
        self.logger.error(repr(failure))

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        try:
            await page.wait_for_timeout(3000)
            content = await page.content()
            
            scripts = re.findall(r'<script [^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', content, re.DOTALL)
            
            if not scripts:
                sel = scrapy.Selector(text=content)
                scripts = sel.xpath('//script[@type="application/ld+json"]/text()').getall()

            item = None
            for raw in scripts:
                raw_clean = raw.strip()
                if not raw_clean or '"Product"' not in raw_clean:
                    continue
                
                try:
                    data = json.loads(raw_clean)
                    objs = data if isinstance(data, list) else [data]
                    
                    for obj in objs:
                        if isinstance(obj, dict) and obj.get('@type') == 'Product':
                            offers = obj.get('offers', {})
                            if isinstance(offers, list) and offers:
                                offers = offers[0]
                            
                            price_val = offers.get('price', 0)
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
                            
                            item = ParsedProduct(
                                title=str(obj.get('name', '')).strip(),
                                price=clean_price,
                                source=urlsplit(response.url).netloc,
                                brand=brand,
                                url=response.url,
                                sku=str(obj.get('sku') or obj.get('mpn') or ""),
                                image_url=img_url,
                                properties=obj
                            )
                            break
                    if item: break
                except:
                    continue

            if item:
                yield item
            else:
                raise Exception("Product content found in HTML but failed to parse as JSON")

        except Exception as e:
            self.logger.error(f"Parse error: {e}")
            raise e
        finally:
            await page.close()