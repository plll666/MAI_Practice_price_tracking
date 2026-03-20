from src.database.database import wait_db

if __name__ == "__main__":
    if wait_db():
        print("Запуск основной логики приложения...")
