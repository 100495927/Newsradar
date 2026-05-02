from __future__ import annotations

from shared.mongo import Database

RSS_WORKER_REQUIRED_COLLECTIONS = (
    "rss_entradas",
    "rss_fuentes",
    "rss_categorias_iptc",
)


def build_rss_worker_db() -> Database:
    return Database(required_collection_names=RSS_WORKER_REQUIRED_COLLECTIONS)


__all__ = ["RSS_WORKER_REQUIRED_COLLECTIONS", "build_rss_worker_db"]
