import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from src.core.logger import logger


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.yandex.ru")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "MAI Price Tracker")
        self.enabled = bool(self.smtp_user and self.smtp_password)

    def send_email(self, to: str, subject: str, html_body: str, max_retries: int = 3) -> bool:
        """Отправить email."""
        if not self.enabled:
            logger.warning(f"SMTP not configured, skipping email to {to}")
            return False

        for attempt in range(max_retries):
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = self.smtp_from
                msg["To"] = to

                html_part = MIMEText(html_body, "html", "utf-8")
                msg.attach(html_part)

                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.smtp_from, to, msg.as_string())

                logger.info(f"Email sent to {to}: {subject}")
                return True

            except Exception as e:
                logger.warning(f"Email attempt {attempt + 1}/{max_retries} failed for {to}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to send email to {to} after {max_retries} attempts")
                    return False

        return False

    def send_price_alert_email(
        self,
        to: str,
        product_title: str,
        product_url: str,
        current_price: float,
        target_price: float,
        image_url: Optional[str] = None
    ) -> bool:
        """Отправить email о падении цены."""
        savings = target_price - current_price

        subject = f"Цена снизилась! {product_title}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2ecc71;">Цена снизилась! 🎉</h2>
            <p>Отслеживаемый товар подешевел:</p>
            <div style="background: #f8f9fa; border-radius: 8px; padding: 16px; margin: 16px 0;">
                {"<img src='" + product_url + "' style='max-width: 200px; margin-bottom: 12px;'/>" if image_url else ""}
                <h3 style="margin: 0 0 8px 0;">{product_title}</h3>
                <p style="margin: 0; font-size: 18px;">
                    <span style="text-decoration: line-through; color: #999;">{target_price:.0f}₽</span>
                    <span style="color: #2ecc71; font-weight: bold;"> → {current_price:.0f}₽</span>
                </p>
                <p style="color: #2ecc71; margin: 8px 0 0 0;">Вы сэкономите {savings:.0f}₽</p>
            </div>
            <a href="{product_url}"
               style="display: inline-block; background: #3498db; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 4px; margin-top: 8px;">
                Посмотреть товар
            </a>
            <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
            <p style="color: #999; font-size: 12px;">
                Вы получили это письмо, потому что отслеживаете товар на сайте MAI Price Tracker.
            </p>
        </body>
        </html>
        """

        return self.send_email(to, subject, html_body)

    def send_product_appeared_email(
        self,
        to: str,
        product_title: str,
        product_url: str,
        current_price: float,
        image_url: Optional[str] = None
    ) -> bool:
        """Отправить email о появлении товара в наличии."""
        subject = f"Товар появился в наличии! {product_title}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #3498db;">Товар появился в наличии! 🎉</h2>
            <p>Отслеживаемый товар снова доступен:</p>
            <div style="background: #f8f9fa; border-radius: 8px; padding: 16px; margin: 16px 0;">
                {"<img src='" + product_url + "' style='max-width: 200px; margin-bottom: 12px;'/>" if image_url else ""}
                <h3 style="margin: 0 0 8px 0;">{product_title}</h3>
                <p style="margin: 0; font-size: 18px; font-weight: bold;">{current_price:.0f}₽</p>
            </div>
            <a href="{product_url}"
               style="display: inline-block; background: #3498db; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 4px; margin-top: 8px;">
                Купить сейчас
            </a>
            <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
            <p style="color: #999; font-size: 12px;">
                Вы получили это письмо, потому что отслеживаете товар на сайте MAI Price Tracker.
            </p>
        </body>
        </html>
        """

        return self.send_email(to, subject, html_body)