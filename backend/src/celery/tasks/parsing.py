import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.celery.app import celery_app
from src.core.logger import logger
from src.database.database import SyncSessionLocal
from src.database.models import ProductLinks, Subscriptions, Users, PriceHistory


def run_spider_sync(url: str) -> dict | None:
    """Запустить ProbeSpider через subprocess."""
    parent = Path(__file__).parent.parent
    tmp_file = parent / f"scrape_{abs(hash(url))}.jsonl"

    process = subprocess.run(
        [sys.executable, "-m", "scrapy", "crawl", "parserpice", "-a", f"url={url}", "-o", str(tmp_file)],
        cwd=str(parent),
        capture_output=True,
        text=True,
        timeout=60
    )

    if process.returncode != 0 or not tmp_file.exists():
        return None

    try:
        with open(tmp_file) as f:
            data = json.loads(f.readline())
        return data
    finally:
        tmp_file.unlink(missing_ok=True)


def get_user_product_links(db: Session, user_id: int) -> list[tuple[int, str]]:
    """Получить связки (link_id, url) для продуктов пользователя."""
    query = (
        select(ProductLinks.id, ProductLinks.url)
        .join(Subscriptions, Subscriptions.product_id == ProductLinks.product_id)
        .where(Subscriptions.user_id == user_id)
    )
    result = db.execute(query)
    return list(result.all())


def get_users_need_parsing(db: Session) -> list[int]:
    """Получить пользователей, которым нужен парсинг."""
    now = datetime.utcnow()
    query = select(Users).where(Users.is_active == True)
    result = db.execute(query)
    users = result.scalars().all()

    users_to_parse = []
    for user in users:
        interval_seconds = user.parse_interval or 3600
        if not user.last_parse_at or (now - user.last_parse_at).total_seconds() >= interval_seconds:
            users_to_parse.append(user.id)

    return users_to_parse


@celery_app.task(bind=True, name="src.celery.tasks.parse_product")
def parse_product_task(self, link_id: int) -> dict[str, Any]:
    """Парсить товар по link_id и сохранить цену в БД."""
    logger.info(f"Starting parse task for link_id: {link_id}")
    db = SyncSessionLocal()
    try:
        result = db.execute(
            select(ProductLinks.url).where(ProductLinks.id == link_id)
        )
        url = result.scalar_one_or_none()
        if not url:
            return {"status": "error", "link_id": link_id, "error": "URL not found"}

        scraped = run_spider_sync(url)
        if not scraped:
            return {"status": "error", "link_id": link_id, "error": "Parse failed"}

        new_price = PriceHistory(link_id=link_id, price=scraped.get('price', 0))
        db.add(new_price)
        db.commit()

        logger.info(f"Parsed {url}: price={scraped.get('price')}")
        return {"status": "success", "link_id": link_id, "price": scraped.get('price')}
    except Exception as e:
        db.rollback()
        logger.error(f"Parse task exception: {link_id}, error: {str(e)}")
        return {"status": "error", "link_id": link_id, "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, name="src.celery.tasks.parse_user_products")
def parse_user_products_task(self, user_id: int) -> dict[str, Any]:
    """Парсить все продукты пользователя."""
    logger.info(f"Starting parse task for user {user_id}")
    db = SyncSessionLocal()
    try:
        links = get_user_product_links(db, user_id)
        logger.info(f"Found {len(links)} products to parse for user {user_id}")

        for link_id, url in links:
            parse_product_task.delay(link_id)

        db.execute(
            update(Users).where(Users.id == user_id).values(last_parse_at=datetime.utcnow())
        )
        db.commit()

        return {"status": "completed", "user_id": user_id, "parsed_count": len(links)}
    except Exception as e:
        db.rollback()
        logger.error(f"Error in parse_user_products_task: {str(e)}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, name="src.celery.tasks.check_users_parse_schedule")
def check_users_parse_schedule_task(self) -> dict[str, Any]:
    """Проверить расписание парсинга пользователей."""
    logger.info("Checking users parse schedule")
    db = SyncSessionLocal()
    try:
        user_ids = get_users_need_parsing(db)
        logger.info(f"Users need parsing: {user_ids}")

        for user_id in user_ids:
            parse_user_products_task.delay(user_id)

        return {"status": "completed", "users_count": len(user_ids)}
    except Exception as e:
        logger.error(f"Error in check_users_parse_schedule_task: {str(e)}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()