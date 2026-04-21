from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import alerts_col, next_mongo_id, notifications_col, users_col
from .models import Alert, AlertCreate, AlertUpdate

router = APIRouter(tags=["alerts"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_user_exists(user_id: int) -> None:
    """Lanza 404 si el usuario no existe."""
    if not users_col.find_one({"id": user_id}):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


def _doc_to_alert(doc: dict) -> Alert:
    """Convierte un documento MongoDB en el modelo público de alerta."""
    return Alert(
        id=doc["id"],
        user_id=doc["user_id"],
        name=doc["name"],
        descriptors=doc.get("descriptors", []),
        categories=doc.get("categories", []),
        cron_expression=doc["cron_expression"],
        enabled=doc.get("enabled", True),
    )


def ensure_alert_for_user(user_id: int, alert_id: int) -> Alert:
    """Comprueba que la alerta exista y pertenezca al usuario indicado."""
    alert = alerts_col.find_one({"id": alert_id, "user_id": user_id}, {"_id": 0})
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    return _doc_to_alert(alert)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}/alerts", response_model=List[Alert])
def list_user_alerts(user_id: int, _: UserInDB = Depends(get_current_user)) -> List[Alert]:
    """Lista alertas de un usuario concreto."""
    ensure_user_exists(user_id)
    return [_doc_to_alert(doc) for doc in alerts_col.find({"user_id": user_id}, {"_id": 0}).sort("id", 1)]


@router.post(
    "/users/{user_id}/alerts",
    response_model=Alert,
    status_code=201,
)
def create_user_alert(
    user_id: int,
    payload: AlertCreate,
    _: UserInDB = Depends(get_current_user),
) -> Alert:
    """Crea una alerta para un usuario (requiere rol gestor)."""
    ensure_user_exists(user_id)

    if not payload.descriptors:
        raise HTTPException(
            status_code=400,
            detail="La alerta debe incluir al menos un descriptor",
        )

    if alerts_col.count_documents({"user_id": user_id}) >= 20:
        raise HTTPException(
            status_code=400,
            detail="Un gestor no puede tener más de 20 alertas",
        )

    now = datetime.now(timezone.utc)
    alert_id = next_mongo_id("alerts")
    alert_doc = {
        "id": alert_id,
        "user_id": user_id,
        **payload.model_dump(),
        "category_id": 0,
        "rss_channel_ids": [],
        "notification_channels": ["app", "email"],
        "enabled": True,
        "last_checked_at": None,
        "last_run_at": None,
        "next_run_at": None,
        "created_at": now,
        "updated_at": now,
    }
    alerts_col.insert_one(alert_doc)
    return _doc_to_alert(alert_doc)


@router.get("/users/{user_id}/alerts/{alert_id}", response_model=Alert)
def get_user_alert(
    user_id: int,
    alert_id: int,
    _: UserInDB = Depends(get_current_user),
) -> Alert:
    """Recupera una alerta concreta de un usuario."""
    return ensure_alert_for_user(user_id, alert_id)


@router.put("/users/{user_id}/alerts/{alert_id}", response_model=Alert)
def update_user_alert(
    user_id: int,
    alert_id: int,
    payload: AlertUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Alert:
    """Actualiza una alerta de usuario."""
    ensure_alert_for_user(user_id, alert_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "descriptors" in update_data and not update_data["descriptors"]:
        raise HTTPException(
            status_code=400,
            detail="La alerta debe incluir al menos un descriptor",
        )

    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        alerts_col.update_one(
            {"id": alert_id, "user_id": user_id},
            {"$set": update_data},
        )

    updated = alerts_col.find_one({"id": alert_id, "user_id": user_id}, {"_id": 0})
    return _doc_to_alert(updated)


@router.delete(
    "/users/{user_id}/alerts/{alert_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
)
def delete_user_alert(
    user_id: int,
    alert_id: int,
    _: UserInDB = Depends(get_current_user),
) -> None:
    """Elimina una alerta y sus notificaciones vinculadas."""
    ensure_alert_for_user(user_id, alert_id)
    notifications_col.delete_many({"alert_id": alert_id})
    alerts_col.delete_one({"id": alert_id, "user_id": user_id})
