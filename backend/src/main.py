import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router
from src.api.products import router as product_router
from src.api.user import router as user_router
from src.api.settings import router as settings_router
from src.api.analytics import router as analytics_router
from src.api.alerts import router as alerts_router
from src.api.telegram import router as telegram_router
from src.core.logger import setup_logging, logger

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")

    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    if webhook_url:
        try:
            from src.services.telegram_service import TelegramService
            service = TelegramService()
            if service.enabled:
                webhook_url = webhook_url.rstrip('/')
                success = service.set_webhook(webhook_url)
                if success:
                    logger.info(f"Webhook auto-set to {webhook_url}")
                else:
                    logger.warning(f"Failed to auto-set webhook to {webhook_url}")
        except Exception as e:
            logger.error(f"Error auto-setting webhook: {e}")
    
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="Price Tracker API",
    lifespan=lifespan,
    redirect_slashes=False
)

origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(user_router)
app.include_router(settings_router)
app.include_router(analytics_router)
app.include_router(alerts_router)
app.include_router(telegram_router)


@app.get("/")
def read_root():
    return {"message": "Service is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )