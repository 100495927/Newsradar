from __future__ import annotations

import os
from typing import Any, Dict

from pymongo import MongoClient

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

# -- In-memory stores (usuarios migrados a MongoDB) --
roles_store: Dict[int, Any] = {}
alerts_store: Dict[int, Any] = {}
categories_store: Dict[int, Any] = {}
notifications_store: Dict[int, Any] = {}
information_sources_store: Dict[int, Any] = {}
rss_channels_store: Dict[int, Any] = {}
stats_store: Dict[int, Any] = {}

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
