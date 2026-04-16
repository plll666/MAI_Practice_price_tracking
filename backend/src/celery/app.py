"""
Конфигурация приложения Celery для отслеживания цен.
"""
import os
from celery import Celery

from src.core.logger import setup_logging, logger
import src.celery.tasks.alerts  # noqa
import src.celery.tasks.maintenance # noqa
import src.celery.tasks.parsing # noqa

setup_logging()

broker_url: str = os.getenv("CELERY_BROKER", "redis://redis:6379/0")
backend_url: str = os.getenv("CELERY_BACKEND", "redis://redis:6379/0")
parse_interval: int = int(os.getenv("PARSE_INTERVAL_SECONDS", "3600"))

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
        "src.celery.tasks.parse_all_products": {"queue": "parsing"},
        "src.celery.tasks.cleanup_old_prices": {"queue": "maintenance"},
        "src.celery.tasks.check_price_alerts": {"queue": "notifications"},
    },
    beat_schedule={
        "parse-all-products": {
            "task": "src.celery.tasks.parse_all_products",
            "schedule": parse_interval,
            "args": (),
        },
        "cleanup-old-prices": {
            "task": "src.celery.tasks.cleanup_old_prices",
            "schedule": 20000000.0,
            "args": (30,),
        },
        "check-price-alerts": {
            "task": "src.celery.tasks.check_price_alerts",
            "schedule": 300.0,
            "args": (),
        },
    },
)

logger.info("Celery Beat конфигурация загружена")
logger.info(f"Broker: {broker_url}")
logger.info(f"Backend: {backend_url}")
logger.info(f"Интервал парсинга: {parse_interval} секунд ({parse_interval // 60} минут)")
logger.info("Запланированные задачи (Beat Schedule):")
for task_name, task_config in celery_app.conf.beat_schedule.items():
    schedule = task_config['schedule']
    if isinstance(schedule, (int, float)):
        schedule_str = f"{int(schedule)} сек ({int(schedule) // 60} мин)"
    else:
        schedule_str = str(schedule)
    logger.info(f"  [{task_name}] {task_config['task']} - каждые {schedule_str}")
logger.info("Очереди задач:")
logger.info("  [parsing] - парсинг товаров")
logger.info("  [maintenance] - очистка старых цен")
logger.info("  [notifications] - проверка алертов")



