from __future__ import annotations

import logging
import threading
from time import sleep

from alerts import process_alerts
from rss.links_estandar import generar_lista_estandar_feeds
from rss.RSSFuente import RSSFuente
from shared.mongo.Database import Database
from worker.Entorno import Entorno
from worker.api_fuentes import api_task

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[rss-worker] %(asctime)s %(levelname)s %(message)s",
    )


def fetch_de_entradas(db: Database) -> None:
    fuentes = db.col_rss_fuentes.lista_fuentes()
    logger.info("Iniciando procesamiento de %d fuentes RSS", len(fuentes))

    total_nuevas = 0
    for fuente in fuentes:
        try:
            for entrada in fuente.obtener_entradas():
                if entrada.categorias_raw:
                    ids_iptc = {
                        db.col_rss_cat_iptc.id_por_nombre(cat_nombre)
                        for cat_nombre in entrada.categorias_raw
                    }
                    
                    entrada.categorias = [i for i in ids_iptc if i is not None]
                if db.col_rss_entradas.insertar(entrada) is not None:
                    total_nuevas += 1
            
            db.col_rss_fuentes.actualizar_categoria_fuente(fuente.url)
            
        except Exception:
            logger.exception("Error crítico en ingesta de fuente: %s", fuente.url)

    logger.info("Ciclo completado. Nuevas entradas detectadas: %d", total_nuevas)


def process_alerts_safely(db: Database) -> int:
    """Ejecuta alertas sin tumbar el ciclo principal del worker."""
    try:
        return process_alerts(db)
    except Exception:
        logger.exception("Fallo el procesamiento de alertas")
        return 0


def importar_categorias_iptc(db: Database):
    from rss.iptc import LOCALIZACION_JSON_IPTC
    import json

    with open(LOCALIZACION_JSON_IPTC, "r", encoding="utf-8") as f:
        datos = json.load(f)

    db.col_rss_cat_iptc.insertar_json(datos)


def main() -> None:
    configure_logging()
    entorno = Entorno()
    db = Database()
    api_hilo = threading.Thread(target=api_task, daemon=True)
    api_hilo.start()

    importar_categorias_iptc(db)

    for feed in generar_lista_estandar_feeds():
        categoria_str = feed.categoria_iptc_string()
        if categoria_str:
            categoria_id = db.col_rss_cat_iptc.id_por_nombre(categoria_str)
            feed.categoria_iptc = categoria_id
        else:
            feed.categoria_iptc = None

        db.col_rss_fuentes.insertar(feed)

    if entorno.run_once == "true":
        fetch_de_entradas(db)
        # Las alertas se evaluan justo despues de ingerir nuevas entradas RSS.
        process_alerts_safely(db)
        return

    while True:
        try:
            fetch_de_entradas(db)
            # Fallos de alertas no deben impedir que el worker siga ingiriendo RSS.
            process_alerts_safely(db)
        except Exception:
            logger.exception("Fallo un ciclo completo de ingesta RSS")
        sleep(entorno.intervalo_rss)


if __name__ == "__main__":
    main()
