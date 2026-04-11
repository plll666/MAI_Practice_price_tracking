import json
import os
import random
import asyncio
from src.repositories.product_repository import ProductRepository
from src.schemas.products import ProductCreate
from src.core.logger import logger
from fastapi import HTTPException

class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo
    async def add_and_parse_product(self, user_id: int, product_data: ProductCreate):
        url_str = str(product_data.url)        
        tmp_filename = f"scraped_{random.randint(100000, 999999)}.jsonl"
        
        try:
            logger.info(f"Запуск парсинга для URL: {url_str}")
            process = await asyncio.create_subprocess_exec(
                "scrapy", "crawl", "parserpice",
                "-a", f"url={url_str}",
                "-o", tmp_filename,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60.0)
            except asyncio.TimeoutError:
                process.kill()
                raise HTTPException(status_code=408, detail="Parsing timeout")

            if process.returncode != 0:
                raise Exception(f"Parser error: {stderr.decode()}")

            scraped_item = None
            if os.path.exists(tmp_filename):
                with open(tmp_filename, "r", encoding="utf-8") as f:
                    line = f.readline()
                    if line:
                        scraped_item = json.loads(line)

            if not scraped_item:
                raise Exception("No data scraped")

            raw_image = scraped_item.get("image_url", "")
            if raw_image.startswith("//"):
                image_url = f"https:{raw_image}"
            elif raw_image and not raw_image.startswith("http"):
                image_url = f"https://{scraped_item.get('source')}{raw_image}"
            else:
                image_url = raw_image
            props = scraped_item.get("properties", {})
            if not isinstance(props, dict):
                props = {}
            keys_to_remove = [
                "image", "image_url", "images", 
                "@context", "@type", "review", 
                "aggregateRating", "offers"
            ]
            for key in keys_to_remove:
                props.pop(key, None)

            product = await self.repo.get_or_create_product_by_url(
                user_id=user_id,
                url=url_str,
                title=scraped_item.get("title") or "Без названия",
                brand=scraped_item.get("brand") or "Unknown",
                price=int(scraped_item.get("price", 0)),
                image_url=image_url,
                properties=props
            )
            return product

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Service Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if os.path.exists(tmp_filename):
                os.remove(tmp_filename)
    async def get_all_products(self, user_id: int):
        return await self.repo.get_all_products(user_id=user_id)
    async def get_product_by_id(self, product_id: int):
        return await self.repo.get_product_by_id(product_id)