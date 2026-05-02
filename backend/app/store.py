from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict

from pymongo import MongoClient, ReturnDocument

# -- MongoDB --
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    (
        f"mongodb://{os.getenv('MONGO_APP_USER', 'newsradar_app')}"
        f":{os.getenv('MONGO_APP_PASSWORD', 'change_me_app_pwd')}"
        f"@{os.getenv('MONGO_HOST', 'mongodb')}:{os.getenv('MONGO_PORT', '27017')}"
        f"/{os.getenv('MONGO_APP_DB', 'newsradar')}"
        f"?authSource={os.getenv('MONGO_APP_DB', 'newsradar')}"
    ),
)
client = MongoClient(MONGODB_URI)
db = client[os.getenv("MONGO_APP_DB", "newsradar")]
users_col = db["users"]
rss_fuentes_col = db["rss_fuentes"]
rss_entradas_col = db["rss_entradas"]
categories_col = db["rss_categorias_iptc"]
stats_col = db["stats"]
alerts_col = db["alerts"]
notifications_col = db["notifications"]
counters_col = db["counters"]

# -- In-memory stores for contract entities that are still not persisted --
roles_store: Dict[int, Any] = {}
categories_store: Dict[int, Any] = {}

counters: Dict[str, int] = {
    "roles": 1,
    "users": 1,
    "alerts": 1,
    "categories": 1,
    "notifications": 1,
    "information_sources": 1,
    "rss_channels": 1,
    "stats": 1,
}


def next_id(counter_key: str) -> int:
    """Genera IDs autoincrementales por tipo de entidad."""
    value = counters[counter_key]
    counters[counter_key] += 1
    return value


def next_mongo_id(counter_key: str) -> int:
    """Genera IDs enteros compartidos entre API y workers usando MongoDB."""
    result = counters_col.find_one_and_update(
        {"_id": counter_key},
        {
            "$inc": {"seq": 1},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(result["seq"])
