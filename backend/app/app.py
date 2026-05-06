from __future__ import annotations

from datetime import datetime, timezone

import pymongo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .alertas.routes import router as alertas_router
from .auth.routes import router as auth_router
from .synonyms.routes import router as synonyms_router
from .auth.user import Role  # noqa: F401 – usado en roles_store
from .category.routes import router as category_router
from .category.models import Category
from .notificaciones.routes import router as notificaciones_router
from .rss.routes import router as rss_router
from .stats.routes import router as stats_router
from shared.iptc_catalog import IPTC_TOP_LEVEL_CATEGORIES
from .store import (
    alerts_col,
    categories_col,
    categories_store,
    counters,
    counters_col,
    notifications_col,
    roles_store,
    information_sources_col,
    rss_channels_col,
    stats_col,
    users_col,
)

API_PREFIX = "/api/v1"
ROLELESS_DEFAULT_ROLE_ID = 1
ROLELESS_DEFAULT_ROLE_NAME = "manager"

app = FastAPI(
    title="NewsRadar API",
    version="1.0.0",
    description="API REST para gestión de usuarios, alertas, notificaciones, fuentes y canales RSS.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Routers --
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(alertas_router, prefix=API_PREFIX)
app.include_router(notificaciones_router, prefix=API_PREFIX)
app.include_router(rss_router, prefix=API_PREFIX)
app.include_router(category_router, prefix=API_PREFIX)
app.include_router(synonyms_router, prefix=API_PREFIX)
app.include_router(stats_router, prefix=f"{API_PREFIX}/stats")


# -- Startup --

def _sync_user_counter_from_mongo() -> None:
    """Alinea el contador de usuarios con el mayor ID persistido en MongoDB."""
    max_doc = users_col.find_one(sort=[("id", pymongo.DESCENDING)])
    if max_doc and isinstance(max_doc.get("id"), int):
        counters["users"] = max_doc["id"] + 1


def _ensure_manager_role() -> int:
    """Mantiene un unico rol funcional de gestor para compatibilidad."""
    roles_store.clear()
    roles_store[ROLELESS_DEFAULT_ROLE_ID] = Role(
        id=ROLELESS_DEFAULT_ROLE_ID,
        name=ROLELESS_DEFAULT_ROLE_NAME,
    )
    counters["roles"] = max(counters["roles"], ROLELESS_DEFAULT_ROLE_ID + 1)
    return ROLELESS_DEFAULT_ROLE_ID


def _verify_required_collections() -> None:
    """Comprueba que las colecciones Mongo usadas por la API ya existen."""
    database = getattr(users_col, "database", None)
    if database is None:
        return

    required_collections = (
        users_col,
        information_sources_col,
        rss_channels_col,
        alerts_col,
        notifications_col,
        categories_col,
        counters_col,
        stats_col,
    )
    existing_collection_names = set(database.list_collection_names())
    missing_collection_names = [
        collection.name
        for collection in required_collections
        if collection.name not in existing_collection_names
    ]
    if missing_collection_names:
        raise RuntimeError(
            "Faltan colecciones requeridas en MongoDB: "
            + ", ".join(sorted(missing_collection_names))
        )


def _seed_static_iptc_categories() -> None:
    """Fallback para contextos sin semilla Mongo inicial."""
    categories_store.clear()
    for category in IPTC_TOP_LEVEL_CATEGORIES:
        categories_store[category.id] = Category(id=category.id, name=category.name, source=category.source)


def _load_iptc_categories_from_mongo() -> None:
    """Carga el catálogo IPTC persistido en MongoDB."""
    docs = list(categories_col.find({}, {"_id": 1, "descripciones": 1}).sort("_id", 1))
    if not docs:
        _seed_static_iptc_categories()
        return

    categories_store.clear()
    for doc in docs:
        descriptions = doc.get("descripciones") or []
        primary_description = descriptions[0] if descriptions else {}
        name = primary_description.get("nombre")
        if not name:
            continue
        categories_store[int(doc["_id"])] = Category(
            id=int(doc["_id"]),
            name=name,
            source="IPTC",
        )


def create_seed_data() -> None:
    """Carga en memoria el catálogo y el rol canónico a partir de Mongo."""
    _verify_required_collections()
    _sync_user_counter_from_mongo()
    _load_iptc_categories_from_mongo()
    _ensure_manager_role()


@app.on_event("startup")
def on_startup() -> None:
    create_seed_data()


@app.get(f"{API_PREFIX}/health", tags=["system"])
def health() -> dict:
    """Healthcheck."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
