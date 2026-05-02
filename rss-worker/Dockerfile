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

WORKDIR /app

CMD ["python", "-m", "rss_worker"]
