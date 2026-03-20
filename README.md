# Price Tracking System
## Database Service

Развертывание базы данных для проекта. Развертывание происходит через Docker
## Технологии
* **Python 3.11** 
* **PostgreSQL**
* **SQLAlchemy**
* **Alembic**
* **Docker & Docker Compose**

## Быстрый старт

### 1. Подготовка окружения
Создайте файл `.env` в корне папки `database` на основе примера, поменяв внутри перемынные окружения:
```bash
cp .env_example .env
```

### 2. Запуск проекта
```
docker-compose up --build
```
### 3. Структура проекта
models.py — описание таблиц.

database.py — конфиг подключения.

migrations/ — история изменений базы.

alembic.ini — настройки инструмента миграций.

### 4. Работа с миграциями
Если меняете models.py создайте новую миграцию:
```
docker-compose run --rm app alembic revision --autogenerate -m "Описание изменений"
```
Затем примените её:
```
docker-compose run --rm app alembic upgrade head
```
