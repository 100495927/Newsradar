FROM python:3.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY backend /app/backend
COPY shared /app/shared
COPY scripts /app/scripts

ENV PYTHONPATH="/app:/app/backend"

EXPOSE 8000

WORKDIR /app/backend

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
