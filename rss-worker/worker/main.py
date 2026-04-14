from __future__ import annotations

import logging
from time import sleep

from rss.links_estandar import generar_lista_estandar_feeds
from rss.RSSFuente import RSSFuente
from shared.mongo import Database, RUNTIME_REQUIRED_COLLECTIONS, RUNTIME_REQUIRED_INDEXES
from worker.Entorno import Entorno

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[rss-worker] %(asctime)s %(levelname)s %(message)s",
    )


def main() -> None:
    configure_logging()
    entorno = Entorno()
    db = Database()
    run_preflight(db)

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


def run_preflight(db: Database) -> None:
    logger.info("Ejecutando preflight de MongoDB")
    db.ping()

    existing_collections = set(db.db_app.list_collection_names())
    missing_collections = [
        name for name in RUNTIME_REQUIRED_COLLECTIONS if name not in existing_collections
    ]
    if missing_collections:
        raise RuntimeError(
            "Faltan colecciones requeridas en MongoDB: "
            + ", ".join(sorted(missing_collections))
        )

    for collection_name, expected_indexes in RUNTIME_REQUIRED_INDEXES.items():
        index_info = db.db_app[collection_name].index_information()
        existing_indexes = set(index_info.keys())
        missing_indexes = [
            name for name in expected_indexes if name not in existing_indexes
        ]
        if missing_indexes:
            raise RuntimeError(
                f"Faltan indices requeridos en {collection_name}: "
                + ", ".join(sorted(missing_indexes))
            )

    logger.info("Preflight de MongoDB completado correctamente")


def fetch_de_entradas(db: Database) -> None:
    fuentes: list[RSSFuente] = db.col_rss_fuentes.lista_fuentes()
    logger.info("Procesando %s fuentes RSS", len(fuentes))

    inserted_entries = 0
    for fuente in fuentes:
        try:
            for entrada in fuente.obtener_entradas():
                resultado = db.col_rss_entradas.insertar(entrada)
                if resultado is not None:
                    inserted_entries += 1
        except Exception:
            logger.exception("Fallo la ingesta para la fuente %s", fuente.url)

    logger.info("Ciclo RSS completado. Nuevas entradas insertadas: %s", inserted_entries)


if __name__ == "__main__":
    main()
