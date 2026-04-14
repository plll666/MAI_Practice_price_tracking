"""
Конфигурация приложения Celery для отслеживания цен.
"""
import os
from celery import Celery

from src.core.logger import setup_logging, logger

setup_logging()

broker_url: str = os.getenv("CELERY_BROKER", "redis://redis:6379/0")
backend_url: str = os.getenv("CELERY_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "price_tracker",
    broker=broker_url,
    backend=backend_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    worker_prefetch_multiplier=1,
    task_routes={
        "src.celery.tasks.parse_product": {"queue": "parsing"},
        "src.celery.tasks.parse_user_products": {"queue": "parsing"},
        "src.celery.tasks.check_users_parse_schedule": {"queue": "parsing"},
        "src.celery.tasks.cleanup_old_prices": {"queue": "maintenance"},
        "src.celery.tasks.check_price_alerts": {"queue": "notifications"},
    },
    beat_schedule={
        "check-users-parse-schedule": {
            "task": "src.celery.tasks.check_users_parse_schedule",
            "schedule": 60.0,
            "args": (),
        },
        "cleanup-old-prices": {
            "task": "src.celery.tasks.cleanup_old_prices",
            "schedule": 86400.0,
            "args": (30,),
        },
        "check-price-alerts": {
            "task": "src.celery.tasks.check_price_alerts",
            "schedule": 60.0,
            "args": (),
        },
    },
)

# ВАЖНО: импортировать модули с задачами
import src.celery.tasks.alerts        # noqa
import src.celery.tasks.maintenance   # noqa
import src.celery.tasks.parsing       # noqa