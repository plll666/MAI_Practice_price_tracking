from fastapi import FastAPI
from src.database.database import wait_db
from src.api.auth import router as auth_router

app = FastAPI(title="Price Tracker API")

# Подключаем роутеры
app.include_router(auth_router)

@app.on_event("startup")
def on_startup():
    if not wait_db():
        print("Не удалось подключиться к БД, приложение может работать некорректно.")

@app.get("/")
def read_root():
    return {"message": "Service is running"}