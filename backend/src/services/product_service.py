from src.repositories.product_repository import ProductRepository
from src.scraper.sourses.citilink import CitilinkScraper
from src.schemas.products import ProductCreate
from src.core.logger import logger
from fastapi import HTTPException, status

class ProductService:
    """Работает с процессом добавления ссылки и её первичного парсинга"""
    def __init__(self, repo: ProductRepository):
        self.repo = repo
        self.scraper = CitilinkScraper()
    
    async def _run_parsing(self,product_id: int, url: str):
        if "citilink.ru" in url:
            try:
                scraped = await self.repo.update_product_details(
                    product_id=product_id,
                    url=url,
                    title=scraped.title,
                    price=float(scraped.price)
                    )
            except Exception as e:
                logger.error(f"Ошибка парсинга {url}: {e}")
            return None

    async def add_and_parse_product(self, product_data: ProductCreate):
        url_str = str(product_data.url)
        try:
            scraped = await self.scraper.scrape(url_str)
        except Exception as e:
            logger.error(f"Скрапер не справился: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bad request: error with url"
            )

        try:
            product = await self.repo.get_or_create_product_by_url(
                url=url_str,
                title=scraped.title,
                price=scraped.price
            )
            return product
        except Exception as e:
            logger.error(f"Error in save db: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")