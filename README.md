# Price Tracking System
## Backend & Database Service

Сервис бэкенда и базы данных для системы мониторинга цен. Реализован на FastAPI с использованием PostgreSQL.

## Технологии
* **Python 3.11** 
* **FastAPI** (Web Framework)
* **PostgreSQL** (Database)
* **SQLAlchemy** (ORM)
* **Alembic** (Migrations)
* **Pydantic** (Validation & Schema)
* **Docker & Docker Compose**

## Быстрый старт

### 1. Подготовка окружения
Создайте файл `.env` в корне проекта на основе примера.

```bash
cp .env_example .env
```
### 2. Запуск приложения
#### Вариант А: Локальный запуск (для разработки)
Создайте виртуальное окружение:
```Bash

    python -m venv .venv
    source .venv/bin/activate  # Для Linux/MacOS
    # .venv\Scripts\activate   # Для Windows
```
Установите зависимости:

```Bash

    pip install -r requirements.txt
```
Запустите сервер:

```Bash

    python src/main.py
```

Сервер будет доступен по адресу: http://localhost:8000

#### Вариант Б: Запуск через Docker

```Bash

docker-compose up --build
```

## API и Документация

Автоматическая документация API доступна после запуска сервера:

    Swagger UI: http://localhost:8000/docs
    ReDoc: http://localhost:8000/redoc

Основные эндпоинты:

    POST /auth/register — Регистрация нового пользователя.
    POST /auth/login — Аутентификация и получение JWT токена.

Структура проекта

    src/api/ — Роутеры и обработчики HTTP-запросов.
    src/core/ — Конфигурация, безопасность (JWT, хеширование) и логирование.
    src/database/ — Подключение к БД и модели SQLAlchemy.
    src/repositories/ — Слой доступа к данным (CRUD операции).
    src/schemas/ — Pydantic-схемы для валидации данных.
    migrations/ — Миграции базы данных (Alembic).

## Работа с миграциями (Alembic)

Если вы изменили models.py, необходимо создать миграцию:

#### Локально:

```Bash

alembic revision --autogenerate -m "Описание изменений"
alembic upgrade head
```

#### Через Docker:

```Bash

docker-compose run --rm app alembic revision --autogenerate -m "Описание изменений"
docker-compose run --rm app alembic upgrade head
```