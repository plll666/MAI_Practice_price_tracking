# Система мониторинга цен

Веб-приложение для отслеживания цен на товары из различных интернет-магазинов с автоматическим парсингом, уведомлениями и аналитикой.

## Возможности

- **Регистрация и авторизация** пользователей с JWT токенами
- **Добавление товаров** по URL со страницы магазина
- **Автоматический парсинг** цен, названий и изображений (Scrapy + Playwright)
- **История цен** с графиками изменения за период
- **Уведомления** о снижении цен до целевой
- **Уведомления** о появлении товара в наличии (цена была 0, стала > 0)
- **Уведомления через Telegram-бота** о событиях по товарам
- **Аналитика** по товарам, магазинам и категориям
- **Настройка интервалов** парсинга для каждого пользователя
- **Адаптивный веб-интерфейс** на React с графиками Recharts

## Технологии

### Frontend
- **React 18** — UI фреймворк
- **Vite** — сборщик
- **CSS Modules** — стилизация
- **React Router** — маршрутизация
- **Recharts** — графики

### Backend
- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy 2.0** — ORM
- **Alembic** — миграции БД
- **Pydantic** — валидация данных
- **Celery** — фоновые задачи
- **Redis** — брокер сообщений

### Парсинг
- **Scrapy** — фреймворк для парсинга
- **Playwright** — браузерная автоматизация
- **Playwright Stealth** — обход защиты от ботов

## Быстрый старт

### 1. Требования

- Docker и Docker Compose
- Git

### 2. Установка

Клонируйте репозиторий и перейдите в директорию проекта:

```bash
git clone <repository_url>
cd MAI_Price_Tracker
```

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

### 3. Запуск

```bash
docker-compose up --build -d
```

После запуска будут доступны:

| Сервис | URL |
|---------|-----|
| Веб-приложение | http://localhost |
| API (Swagger) | http://localhost/api/docs |
| API (ReDoc) | http://localhost/api/redoc |
| База данных (PostgreSQL) | `localhost:45432` |
| Redis | `localhost:6379` |

### 4. Остановка

```bash
docker-compose down
```

## Переменные окружения

Скопируйте `.env.example` в `.env` и настройте значения:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `POSTGRES_USER` | Пользователь БД | `tracker_user` |
| `POSTGRES_PASSWORD` | Пароль БД | `your_password` |
| `POSTGRES_DB` | Имя базы данных | `price_tracker` |
| `SECRET_KEY` | Секретный ключ для JWT | `change_this_secret` |
| `ALGORITHM` | Алгоритм шифрования | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена (мин) | `30` |
| `HASHIDS_SALT` | Соль для кодирования ID | `your_salt_here` |
| `HASHIDS_MIN_LENGTH` | Минимальная длина хеша | `8` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `LOG_DIR` | Директория логов | `logs` |
| `SQL_ECHO` | Логирование SQL запросов | `false` |
| `PARSE_INTERVAL_SECONDS` | Интервал парсинга (сек) | `3600` |
| `CELERY_BROKER` | Redis URL для Celery | `redis://redis:6379/0` |
| `CELERY_BACKEND` | Redis URL для результатов | `redis://redis:6379/0` |
| `SMTP_HOST` | SMTP сервер | `smtp.yandex.ru` |
| `SMTP_PORT` | Порт SMTP | `465` |
| `SMTP_USER` | Email для отправки уведомлений | `your_email@yandex.ru` |
| `SMTP_PASSWORD` | Пароль приложения SMTP | `app_password` |
| `SMTP_FROM` | Имя отправителя | `MAI Price Tracker` |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | `bot_token_here` |
| `TELEGRAM_WEBHOOK_ENABLED` | Включить вебхук | `false` |
| `TELEGRAM_WEBHOOK_URL` | URL вебхука | `https://yourdomain.com/api/telegram/webhook` |

## Структура проекта

```
MAI_Price_Tracker/
├── backend/                    # FastAPI бэкенд
│   └── src/
│       ├── api/                # Роутеры (auth, products, alerts, etc.)
│       ├── celery/             # Celery задачи и планировщик
│       ├── core/               # Конфиг, безопасность, JWT, логирование
│       ├── database/           # Подключение к БД, модели SQLAlchemy
│       ├── repositories/       # CRUD операции
│       ├── schemas/            # Pydantic схемы
│       ├── scraper/            # Парсеры (Scrapy + Playwright)
│       ├── services/           # Бизнес-логика
│       └── main.py             # Точка входа
├── frontend/                   # React SPA
│   └── src/
│       ├── components/         # Переиспользуемые компоненты
│       ├── context/            # React Context (AuthContext)
│       ├── lib/                # API клиент, утилиты
│       ├── pages/              # Страницы приложения
│       ├── App.jsx             # Главный компонент
│       └── main.jsx            # Точка входа
├── docker-compose.yml          # Docker Compose (локальная разработка)
├── docker-compose.prod.yml     # Docker Compose (продакшен)
├── .env.example                # Пример переменных окружения
└── README.md                   # Этот файл
```

## API эндпоинты

### Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|---------|
| POST | `/auth/register` | Регистрация нового пользователя |
| POST | `/auth/login` | Авторизация (получение JWT токена) |

### Товары

| Метод | Эндпоинт | Описание |
|-------|----------|---------|
| GET | `/products/` | Список товаров пользователя |
| GET | `/products/{id}` | Информация о товаре |
| GET | `/products/prices` | Текущие цены всех товаров |
| GET | `/products/{id}/history` | История цен товара |
| POST | `/products/new_link` | Добавить товар по URL |
| POST | `/products/{id}/target-price` | Установить целевую цену |
| DELETE | `/products/{id}` | Удалить товар |

### Уведомления

| Метод | Эндпоинт | Описание |
|-------|----------|---------|
| GET | `/alerts/` | Список уведомлений |
| GET | `/alerts/unread-count` | Количество непрочитанных |
| POST | `/alerts/{id}/read` | Отметить как прочитанное |
| POST | `/alerts/read-all` | Отметить все как прочитанные |

### Аналитика

| Метод | Эндпоинт | Описание |
|-------|----------|---------|
| GET | `/analytics` | Общая статистика |

### Настройки

| Метод | Эндпоинт | Описание |
|-------|----------|---------|
| GET | `/settings/parse-interval` | Получить интервал парсинга |
| POST | `/settings/parse-interval` | Установить интервал парсинга |
| GET | `/users/me/contacts` | Получить контакты |
| POST | `/users/me/contacts` | Сохранить контакты |

