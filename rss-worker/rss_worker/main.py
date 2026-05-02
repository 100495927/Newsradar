from __future__ import annotations

import logging
import threading

from api_fuentes import api_task

LOGGER_NOMBRE = "rssworker"
logger = logging.getLogger(LOGGER_NOMBRE)


def fetch_de_entradas() -> None:
    from fetch_pipeline import fetch_de_entradas as _fetch_de_entradas

    _fetch_de_entradas()

def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[rss-worker] %(asctime)s %(levelname)s %(message)s",
    )


def main() -> None:
    configure_logging()
    api_hilo = threading.Thread(target=api_task, daemon=True)
    api_hilo.start()
    from fetch_pipeline import fetch_entradas_task

    fetch_entradas_task()

if __name__ == "__main__":
    main()
