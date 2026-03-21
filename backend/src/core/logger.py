import logging
import sys

# Формат логов: Время - Уровень - Сообщение
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)  # Вывод в консоль
        ]
    )



logger = logging.getLogger("price_tracker")