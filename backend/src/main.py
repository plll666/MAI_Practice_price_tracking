import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.auth import router as auth_router
from src.api.products import router as product_router
from src.api.user import router as user_router
from src.core.logger import setup_logging, logger

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
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

# Подключаем все роутеры
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(user_router)


@app.get("/")
def read_root():
    return {"message": "Service is running"}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )