from __future__ import annotations

import logging

from shared.mongo import RUNTIME_REQUIRED_COLLECTIONS, RUNTIME_REQUIRED_INDEXES
from shared.mongo.Database import Database


def configure_logging(worker_name: str) -> None:
    """Configura un formato de logs consistente para cada worker."""
    logging.basicConfig(
        level=logging.INFO,
        format=f"[{worker_name}] %(asctime)s %(levelname)s %(message)s",
    )


def run_preflight(db: Database) -> None:
    """Valida colecciones e indices requeridos antes de arrancar el worker."""
    logger = logging.getLogger(__name__)
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
