FROM python:3.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY rss-worker/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY rss-worker /app/rss-worker
COPY shared /app/shared

ENV PYTHONPATH="/app:/app/rss-worker"

WORKDIR /app/rss-worker

CMD ["python", "/app/rss-worker/rss_worker/main.py"]
