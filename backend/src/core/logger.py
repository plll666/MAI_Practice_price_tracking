import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    log_level: str = None,
    log_file: str = "app.log",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    file_output: bool = False
):
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    file_output = file_output or os.getenv("LOG_FILE_OUTPUT", "false").lower() == "true"

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, datefmt=date_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if file_output:
        log_dir = os.getenv("LOG_DIR", "logs")
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        log_file_path = log_path / log_file

        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    suppress_loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "uvicorn.access",
        "celery",
        "celery.worker",
        "celery.app",
        "celery.utils",
        "scrapy",
        "scrapy.extensions",
        "scrapy.middleware",
        "selenium",
        "playwright",
        "sqlalchemy",
        "sqlalchemy.engine",
        "sqlalchemy.engine.Engine",
        "sqlalchemy.pool",
        "alembic",
        "alembic.runtime",
        "alembic.runtime.migration",
        "asyncio",
    ]

    for logger_name in suppress_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


logger = logging.getLogger("price_tracker")
