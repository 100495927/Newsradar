from __future__ import annotations

import logging
import threading
from time import sleep

from rss.links_estandar import generar_lista_estandar_feeds
from rss.RSSFuente import RSSFuente
from rss_worker.api_fuentes import api_task
from rss_worker.settings import RssWorkerSettings
from runtime_common import configure_logging, run_preflight
from shared.mongo.Database import Database

logger = logging.getLogger(__name__)


def fetch_de_entradas(db: Database) -> None:
    fuentes: list[RSSFuente] = db.col_rss_fuentes.lista_fuentes()
    logger.info("Procesando %s fuentes RSS", len(fuentes))

    inserted_entries = 0
    for fuente in fuentes:
        if fuente.activo is False:
            continue
        try:
            for entrada in fuente.obtener_entradas():
                resultado = db.col_rss_entradas.insertar(entrada)
                if resultado is not None:
                    inserted_entries += 1
        except Exception:
            logger.exception("Fallo la ingesta para la fuente %s", fuente.url)

    logger.info("Ciclo RSS completado. Nuevas entradas insertadas: %s", inserted_entries)


def main() -> None:
    configure_logging("rss-worker")
    settings = RssWorkerSettings.from_env()
    db = Database()
    run_preflight(db)

    api_hilo = threading.Thread(target=api_task, daemon=True)
    api_hilo.start()

    for feed in generar_lista_estandar_feeds():
        db.col_rss_fuentes.insertar(feed)

    if settings.run_once == "true":
        fetch_de_entradas(db)
        return

    while True:
        try:
            fetch_de_entradas(db)
        except Exception:
            logger.exception("Fallo un ciclo completo de ingesta RSS")
        sleep(float(settings.intervalo_rss))


if __name__ == "__main__":
    main()
