from __future__ import annotations

import logging
from time import sleep

from shared.mongo import Database
from .settings import RssWorkerSettings

LOGGER_NOMBRE = "rssworker"
logger = logging.getLogger(LOGGER_NOMBRE)

def fetch_de_entradas(db: Database) -> int:
    fuentes = db.col_rss_channels.lista_canales_activos()
    logger.info("Iniciando procesamiento de %d canales RSS", len(fuentes))

    total_nuevas = 0
    for fuente in fuentes:
        try:
            for entrada in fuente.obtener_entradas():
                if db.col_rss_entradas.insertar(entrada) is not None:
                    total_nuevas += 1

        except Exception:
            logger.exception("Error critico en ingesta del canal RSS: %s", fuente.url)

    logger.info("Ciclo completado. Nuevas entradas detectadas: %d", total_nuevas)
    return total_nuevas

def fetch_entradas_task(db: Database, settings: RssWorkerSettings) -> None:
    fetch_de_entradas(db)

    while not settings.rss_run_once:
        sleep(settings.intervalo_rss)
        try:
            fetch_de_entradas(db)
        except Exception:
            logger.exception("Fallo un ciclo completo de ingesta RSS")

__all__ = ["fetch_de_entradas", "fetch_entradas_task"]

