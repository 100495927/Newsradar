from __future__ import annotations

import logging

from .fetch_pipeline import fetch_entradas_task
from .runtime import build_rss_worker_db
from .settings import RssWorkerSettings

logger = logging.getLogger("rssworker")

def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[rss-worker] %(asctime)s %(levelname)s %(message)s",
    )


def main() -> None:
    configure_logging()
    settings = RssWorkerSettings.from_env()
    db = build_rss_worker_db()
    logger.info("Colecciones RSS verificadas correctamente en MongoDB")
    fetch_entradas_task(db, settings)

if __name__ == "__main__":
    main()
