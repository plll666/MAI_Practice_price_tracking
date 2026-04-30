import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from src.celery.app import celery_app
from src.core.logger import logger
from src.repositories.celery_sync_repository import CelerySyncRepository


def run_spider_sync(url: str) -> dict | None:
    """Запустить ProbeSpider через subprocess."""
    parent = Path(__file__).parent.parent
    tmp_file = parent / f"scrape_{abs(hash(url))}.jsonl"
    
    if tmp_file.exists():
        tmp_file.unlink()

    logger.info(f"[run_spider] Запуск парсинга: {url[:80]}...")
    
    process = subprocess.run(
        [sys.executable, "-m", "scrapy", "crawl", "parserpice", "-a", f"url={url}", "-o", str(tmp_file)],
        cwd=str(parent),
        capture_output=True,
        text=True,
        timeout=90
    )

    if process.returncode != 0:
        logger.error(f"[run_spider] Scrapy вернул код {process.returncode} для {url[:80]}")
        if process.stderr:
            logger.error(f"[run_spider] stderr: {process.stderr[:2000]}")
            stderr_file = parent / f"scrapy_error_{abs(hash(url))}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(stderr_file, "w", encoding="utf-8") as sf:
                sf.write(process.stderr)
            logger.info(f"[run_spider] Полный stderr сохранён в: {stderr_file}")
        return None

    if not tmp_file.exists():
        logger.warning(f"[run_spider] Файл результата не создан для {url[:80]}")
        if process.stderr:
            debug_file = parent / f"scrapy_debug_{abs(hash(url))}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(debug_file, "w", encoding="utf-8") as df:
                df.write(f"=== STDOUT ===\n{process.stdout}\n\n=== STDERR ===\n{process.stderr}")
            logger.info(f"[run_spider] Stdout/stderr сохранены для отладки: {debug_file}")
        return None

    try:
        with open(tmp_file) as f:
            line = f.readline()
            if not line:
                logger.warning(f"[run_spider] Пустой файл результата для {url[:80]}")
                return None
            data = json.loads(line)
            logger.info(f"[run_spider] Успешно: {url[:80]}, price={data.get('price')}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"[run_spider] Невалидный JSON для {url[:80]}: {e}")
        return None
    finally:
        tmp_file.unlink(missing_ok=True)


@celery_app.task(bind=True, name="src.celery.tasks.parse_product")
def parse_product_task(self, link_id: int) -> dict[str, Any]:
    """Парсить товар по link_id и сохранить цену в БД."""
    logger.info(f"[parse_product] Начало парсинга товара link_id={link_id}")
    
    repo = CelerySyncRepository()
    
    links = repo.get_all_active_links()
    link_dict = {lid: url for lid, url in links}
    
    url = link_dict.get(link_id)
    if not url:
        logger.warning(f"[parse_product] URL не найден для link_id={link_id}")
        return {"status": "error", "link_id": link_id, "error": "URL not found"}

    try:
        logger.info(f"[parse_product] Парсинг URL: {url[:80]}...")
        scraped = run_spider_sync(url)
        
        if not scraped:
            logger.warning(f"[parse_product] Парсинг не удался для link_id={link_id}")
            return {"status": "error", "link_id": link_id, "error": "Parse failed"}

        price = scraped.get('price', 0)
        repo.add_price_record(link_id, price)
        logger.info(f"[parse_product] Успешно! link_id={link_id}, цена={price}")
        
        return {"status": "success", "link_id": link_id, "price": price}
    except Exception as e:
        logger.error(f"[parse_product] Ошибка парсинга link_id={link_id}: {str(e)}")
        return {"status": "error", "link_id": link_id, "error": str(e)}


@celery_app.task(bind=True, name="src.celery.tasks.parse_user_products")
def parse_user_products_task(self, user_id: int) -> dict[str, Any]:
    """Парсить все продукты пользователя."""
    logger.info(f"[parse_user_products] Начало парсинга для пользователя user_id={user_id}")
    
    repo = CelerySyncRepository()
    
    try:
        links = repo.get_user_links(user_id)
        logger.info(f"[parse_user_products] Найдено {len(links)} товаров для user_id={user_id}")
        
        if not links:
            logger.info(f"[parse_user_products] Нет товаров для парсинга user_id={user_id}")
            repo.update_last_parse_at(user_id)
            return {"status": "completed", "user_id": user_id, "parsed_count": 0}

        for link_id, url in links:
            parse_product_task.delay(link_id)
        
        repo.update_last_parse_at(user_id)
        logger.info(f"[parse_user_products] Задачи созданы для {len(links)} товаров user_id={user_id}")

        return {"status": "completed", "user_id": user_id, "parsed_count": len(links)}
    except Exception as e:
        logger.error(f"[parse_user_products] Ошибка для user_id={user_id}: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(bind=True, name="src.celery.tasks.check_users_parse_schedule")
def check_users_parse_schedule_task(self) -> dict[str, Any]:
    """Проверить расписание парсинга пользователей."""
    logger.info(f"[check_schedule] Проверка расписания пользователей")
    
    repo = CelerySyncRepository()
    
    try:
        parse_interval = int(os.getenv("PARSE_INTERVAL_SECONDS", "3600"))
        user_ids = repo.get_users_need_parsing(parse_interval)
        
        if not user_ids:
            logger.info(f"[check_schedule] Нет пользователей для парсинга")
        else:
            logger.info(f"[check_schedule] Запуск парсинга для {len(user_ids)} пользователей: {user_ids}")
        
        for user_id in user_ids:
            parse_user_products_task.delay(user_id)

        return {"status": "completed", "users_count": len(user_ids)}
    except Exception as e:
        logger.error(f"[check_schedule] Ошибка: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(bind=True, name="src.celery.tasks.parse_all_products")
def parse_all_products_task(self) -> dict[str, Any]:
    """Парсить все товары из таблицы ProductLinks."""

    logger.info("[parse_all] Celery Beat: Задача 'parse_all_products' запущена")
    
    repo = CelerySyncRepository()
    
    try:
        links = repo.get_all_active_links()
        logger.info(f"[parse_all] Найдено товаров для парсинга: {len(links)}")

        if not links:
            logger.info("[parse_all] Нет товаров для парсинга")

            return {"status": "completed", "parsed": 0, "errors": 0}

        parsed_count = 0
        error_count = 0
        
        for i, (link_id, url) in enumerate(links, 1):
            try:
                scraped = run_spider_sync(url)
                if scraped:
                    repo.add_price_record(link_id, scraped.get('price', 0))
                    parsed_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"[parse_all] Ошибка парсинга link_id={link_id}: {str(e)}")
                error_count += 1

        logger.info(f"[parse_all] Результат: успешно={parsed_count}, ошибки={error_count}")

        
        return {"status": "completed", "parsed": parsed_count, "errors": error_count}
    except Exception as e:
        logger.error(f"[parse_all] Критическая ошибка: {str(e)}")

        return {"status": "error", "error": str(e)}


@celery_app.task(bind=True, name="src.celery.tasks.parse_url")
def parse_url_task(self, url: str, user_id: int) -> dict[str, Any]:
    """Парсить товар по URL и сохранить в БД. Возвращает данные для сохранения."""
    logger.info(f"[parse_url] Начало парсинга URL: {url[:80]}...")
    
    repo = CelerySyncRepository()
    
    try:
        scraped = run_spider_sync(url)
        
        if not scraped:
            logger.warning(f"[parse_url] Парсинг не удался для URL: {url[:80]}")
            return {"status": "error", "error": "Parse failed", "url": url}
        
        price = scraped.get('price', 0)
        
        raw_image = scraped.get("image_url", "")
        if raw_image.startswith("//"):
            image_url = f"https:{raw_image}"
        elif raw_image and not raw_image.startswith("http"):
            image_url = f"https://{scraped.get('source')}{raw_image}"
        else:
            image_url = raw_image
            
        props = scraped.get("properties", {})
        if not isinstance(props, dict):
            props = {}
        keys_to_remove = ["image", "image_url", "images", "@context", "@type", "review", "aggregateRating", "offers"]
        for key in keys_to_remove:
            props.pop(key, None)
        
        result_data = {
            "status": "success",
            "url": url,
            "user_id": user_id,
            "title": scraped.get("title") or "Без названия",
            "brand": scraped.get("brand") or "Unknown",
            "price": int(price),
            "image_url": image_url,
            "properties": props,
        }
        
        logger.info(f"[parse_url] Успешно! URL: {url[:80]}, цена={price}")
        return result_data
        
    except Exception as e:
        logger.error(f"[parse_url] Ошибка парсинга URL: {url[:80]}: {str(e)}")
        return {"status": "error", "error": str(e), "url": url}
