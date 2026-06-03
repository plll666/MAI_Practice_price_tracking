import pytest
from unittest.mock import MagicMock, patch
from src. services. email_service import EmailService
from src. services. telegram_service import TelegramService

class TestEmailService:
    def test_send_email_disabled(self):
        service = EmailService()
        service.smtp_server = MagicMock()
        service.smtp_server.sendmail = MagicMock()
        service.enabled = False
        
        result = service.send_email("test@test.com", "Subject", "Body")
        assert result == False

class TestTelegramService:
    def test_send_message_success(self):
        service = TelegramService()
        service.enabled = True 
        service.api_url = "https://api.telegram.org/bot123"
        with patch("src.services.telegram_service.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status = MagicMock()

            result = service.send_message("123456", "Test message")
            assert result == True

    def test_send_message_failure(self):
        service = TelegramService()
        service.enabled = True
        service.api_url = "https://api.telegram.org/bot123"
        with patch("src.services.telegram_service.requests.post") as mock_post:
            mock_post.side_effect = Exception("Connection error")

            result = service.send_message("123456", "Test message")
            assert result == False
