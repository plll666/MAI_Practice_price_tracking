import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.auth import router as auth_router
from src.api.products import router as product_router
from src.core.logger import setup_logging, logger

# 1. Настраиваем логирование при старте
setup_logging()


# 2. Lifespan - способ управления событиями
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


# 3. Создаем приложение с lifespan
app = FastAPI(
    title="Price Tracker API",
    lifespan=lifespan
)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(product_router)


@app.get("/")
def read_root():
    return {"message": "Service is running"}


# 4. Запуск сервера
if __name__ == "__main__":
    # Теперь при запуске python src/main.py сервер будет висеть и слушать порт
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )