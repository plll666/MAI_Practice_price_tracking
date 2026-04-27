FROM python:3.11-slim

WORKDIR /app

ARG INSTALL_PLAYWRIGHT=false

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN if [ "$INSTALL_PLAYWRIGHT" = "true" ]; then \
    playwright install-deps chromium && \
    playwright install chromium; \
    fi

COPY . .