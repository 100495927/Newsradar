from __future__ import annotations

import logging
from time import sleep

from rss.links_estandar import generar_lista_estandar_feeds
from rss.RSSFuente import RSSFuente
from worker.Entorno import Entorno
from shared.mongo.Database import Database
import threading
from worker.api_fuentes import api_task

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[rss-worker] %(asctime)s %(levelname)s %(message)s",
    )


def fetch_de_entradas(db: Database) -> None:
    fuentes: list[RSSFuente] = db.col_rss_fuentes.lista_fuentes()
    logger.info("Procesando %s fuentes RSS", len(fuentes))

    inserted_entries = 0
    for fuente in fuentes:
        if fuente.activo == False:
            pass
        try:
            for entrada in fuente.obtener_entradas():
                resultado = db.col_rss_entradas.insertar(entrada)
                if resultado is not None:
                    inserted_entries += 1
        except Exception:
            logger.exception(f"Fallo la ingesta para la fuente {fuente.medio}, {fuente.rss}")

    logger.info("Ciclo RSS completado. Nuevas entradas insertadas: %s", inserted_entries)

# In worker/main.py

def main() -> None:
    configure_logging()
    entorno = Entorno()
    db = Database()
    
    api_hilo = threading.Thread(target=api_task, daemon=True)
    api_hilo.start()

    for feed in generar_lista_estandar_feeds():
        db.col_rss_fuentes.insertar(feed)

    if entorno.run_once == "true":
        fetch_de_entradas(db)
        return

    while True:
        try:
            fetch_de_entradas(db)
        except Exception:
            logger.exception("Fallo un ciclo completo de ingesta RSS")
        sleep(float(entorno.intervalo_rss))

if __name__ == "__main__":
    main()
