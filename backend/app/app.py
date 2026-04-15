from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI

from .alertas.routes import router as alertas_router
from .category.routes import router as category_router
from .auth.routes import router as auth_router
from .auth.user import Role, UserInDB
from .notificaciones.routes import router as notificaciones_router
from .rss.routes import router as rss_router
from .stats.routes import router as stats_router
from .store import next_id, roles_store, users_store

API_PREFIX = "/api/v1"

app = FastAPI(
    title="NewsRadar API",
    version="1.0.0",
    description="API REST para gestión de usuarios, alertas, notificaciones, fuentes y canales RSS.",
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
    """Carga datos semilla (roles y admin) en el arranque si no existen."""
    if roles_store:
        return

    admin_role_id = next_id("roles")
    roles_store[admin_role_id] = Role(id=admin_role_id, name="admin")

    user_role_id = next_id("roles")
    roles_store[user_role_id] = Role(id=user_role_id, name="user")

    admin_user_id = next_id("users")
    users_store[admin_user_id] = UserInDB(
        id=admin_user_id,
        email="admin@newsradar.com",
        first_name="Admin",
        last_name="NewsRadar",
        organization="NewsRadar",
        role_ids=[admin_role_id],
        password="admin123",
    )


@app.on_event("startup")
def on_startup() -> None:
    create_seed_data()


@app.get(f"{API_PREFIX}/health", tags=["system"])
def health() -> dict:
    """Healthcheck."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
