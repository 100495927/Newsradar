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
from .store import counters, next_id, roles_store, users_col

API_PREFIX = "/api/v1"

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
app.include_router(stats_router, prefix=API_PREFIX)


# -- Startup --

def create_seed_data() -> None:
    """Carga roles en memoria y crea el admin en MongoDB si no existe."""
    if roles_store:
        return

    admin_role_id = next_id("roles")
    roles_store[admin_role_id] = Role(id=admin_role_id, name="admin")

    user_role_id = next_id("roles")
    roles_store[user_role_id] = Role(id=user_role_id, name="user")

    if not users_col.find_one({"email": "admin@newsradar.com"}):
        now = datetime.now(timezone.utc)
        admin_id = next_id("users")
        users_col.insert_one({
            "id": admin_id,
            "email": "admin@newsradar.com",
            "first_name": "Admin",
            "last_name": "NewsRadar",
            "organization": "NewsRadar",
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "status": "active",
            "created_at": now,
            "updated_at": now,
        })


@app.on_event("startup")
def on_startup() -> None:
    # Sincronizar el counter de usuarios con el max id en MongoDB
    max_doc = users_col.find_one(sort=[("id", pymongo.DESCENDING)])
    if max_doc:
        counters["users"] = max_doc["id"] + 1

    create_seed_data()


@app.get(f"{API_PREFIX}/health", tags=["system"])
def health() -> dict:
    """Healthcheck."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
