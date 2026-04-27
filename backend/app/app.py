from __future__ import annotations

from datetime import datetime, timezone

import pymongo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .alertas.routes import router as alertas_router
from .auth.routes import router as auth_router
from .auth.user import Role  # noqa: F401 – usado en roles_store
from .category.routes import router as category_router
from .notificaciones.routes import router as notificaciones_router
from .rss.routes import router as rss_router
from .stats.routes import router as stats_router
from .auth.jwt_utils import hash_password
from .category.models import Category
from .rss.iptc_utils import IPTC_TOP_LEVEL_CATEGORIES
from .store import categories_store, counters, next_id, roles_store, users_col

API_PREFIX = "/api/v1"

DEFAULT_USERS = (
    {
        "email": "AdminDefault@newsradar.com",
        "legacy_emails": ["AdminDefault@newsradar.local"],
        "first_name": "AdminDefault",
        "last_name": "NewsRadar",
        "organization": "NewsRadar",
        "role_name": "manager",
        "stored_role": "manager",
    },
    {
        "email": "GestorDefault@newsradar.com",
        "legacy_emails": ["GestorDefault@newsradar.local"],
        "first_name": "GestorDefault",
        "last_name": "NewsRadar",
        "organization": "NewsRadar",
        "role_name": "manager",
        "stored_role": "manager",
    },
    {
        "email": "LectorDefault@newsradar.com",
        "legacy_emails": ["LectorDefault@newsradar.local"],
        "first_name": "LectorDefault",
        "last_name": "NewsRadar",
        "organization": "NewsRadar",
        "role_name": "reader",
        "stored_role": "reader",
    },
)

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
app.include_router(stats_router, prefix=f"{API_PREFIX}/stats")


# -- Startup --

def _sync_user_counter_from_mongo() -> None:
    """Alinea el contador de usuarios con el mayor ID persistido en MongoDB."""
    max_doc = users_col.find_one(sort=[("id", pymongo.DESCENDING)])
    if max_doc and isinstance(max_doc.get("id"), int):
        counters["users"] = max_doc["id"] + 1


def _get_role_id(role_name: str) -> int | None:
    for role_id, role in roles_store.items():
        if role.name == role_name:
            return role_id
    return None


def _next_seed_id(counter_key: str) -> int:
    value = counters[counter_key]
    counters[counter_key] += 1
    return value


def _ensure_role(role_name: str) -> int:
    role_id = _get_role_id(role_name)
    if role_id is not None:
        return role_id

    role_id = _next_seed_id("roles")
    roles_store[role_id] = Role(id=role_id, name=role_name)
    return role_id


def _find_seeded_user(user_data: dict[str, object]) -> dict | None:
    email_candidates = [user_data["email"], *user_data.get("legacy_emails", [])]
    for email in email_candidates:
        existing_user = users_col.find_one({"email": email})
        if existing_user:
            return existing_user
    return None


def _seed_default_user(user_data: dict[str, object]) -> None:
    role_id = _get_role_id(user_data["role_name"])
    if role_id is None:
        return

    now = datetime.now(timezone.utc)
    existing_user = _find_seeded_user(user_data)
    if existing_user:
        users_col.update_one(
            {"email": existing_user["email"]},
            {
                "$set": {
                    "email": user_data["email"],
                    "role_ids": [role_id],
                    "role": user_data["stored_role"],
                    "updated_at": now,
                }
            },
        )
        return

    user_id = _next_seed_id("users")
    users_col.insert_one(
        {
            "id": user_id,
            "email": user_data["email"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "organization": user_data["organization"],
            "password_hash": hash_password("NewsRadar2026"),
            "role_ids": [role_id],
            "created_at": now,
            "updated_at": now,
            "role": user_data["stored_role"],
            "status": "active",
            "is_verified": True,
        }
    )


def _seed_iptc_categories() -> None:
    """Populates categories_store with the 15 standard IPTC top-level categories."""
    if categories_store:
        return
    for name in IPTC_TOP_LEVEL_CATEGORIES:
        category_id = next_id("categories")
        categories_store[category_id] = Category(id=category_id, name=name, source="IPTC")


def create_seed_data() -> None:
    """Carga roles base y usuarios por defecto en el arranque si no existen."""
    _sync_user_counter_from_mongo()
    _seed_iptc_categories()

    for role_name in ("manager", "reader"):
        _ensure_role(role_name)

    for user_data in DEFAULT_USERS:
        _seed_default_user(user_data)


@app.on_event("startup")
def on_startup() -> None:
    create_seed_data()


@app.get(f"{API_PREFIX}/health", tags=["system"])
def health() -> dict:
    """Healthcheck."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
