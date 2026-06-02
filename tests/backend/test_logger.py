import pytest
from src.core.logger import setup_logging, logger

class TestLogger:
    
    def test_setup_logging(self):
        setup_logging()
        assert logger is not None

    def test_logger_info(self):
        logger.info("Test info message")
        assert True

    def test_logger_error(self):
        logger.error("Test error message")
        assert True