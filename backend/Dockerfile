FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

FROM base AS with-playwright
RUN .venv/bin/playwright install && \
    .venv/bin/playwright install-deps chromium

FROM with-playwright AS app
COPY . .

FROM with-playwright AS worker
COPY . .