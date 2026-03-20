import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

load_dotenv(".env_db") 

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")
host = os.getenv("DB_HOST", "db") 
port = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(DATABASE_URL)

def wait_db():
    for i in range(5):
        try:
            print(f"Проверка связи с БД ({i+1}/5)...")
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("База доступна")
            return True
        except OperationalError:
            print("База еще загружается. Ждем 3 секунды...")
            time.sleep(3)
    
    print("Error: база так и не ответила.")
    return False
