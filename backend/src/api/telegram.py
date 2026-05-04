from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.services.telegram_handler import TelegramHandler
from src.services.telegram_service import TelegramService

router = APIRouter(prefix="/telegram", tags=["Telegram"])

@router.post("/webhook")
async def telegram_webhook(update: dict, db: AsyncSession = Depends(get_db)):
    handler = TelegramHandler()
    await handler.process_update(update, db)
    return JSONResponse(content={"ok": True})

@router.post("/set-webhook")
async def set_webhook(url: str):
    service = TelegramService()
    if service.set_webhook(url):
        return {"ok": True, "message": f"Webhook set to {url}"}
    return {"ok": False, "message": "Failed to set webhook"}

@router.get("/webhook-info")
async def get_webhook_info():
    service = TelegramService()
    info = service.get_webhook_info()
    if info:
        return info
    return {"ok": False, "message": "Failed to get webhook info"}
