from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..alertas.routes import ensure_alert_for_user
from ..auth.user import UserInDB
from ..dependencies import ensure_gestor_role, ensure_user_can_access, get_current_user
from ..store import alerts_col, next_mongo_id, notifications_col
from .models import (
    Notification,
    NotificationCreate,
    NotificationMailboxItem,
    NotificationMatch,
    NotificationReadState,
    NotificationUpdate,
)

router = APIRouter(tags=["notifications"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _doc_to_notification(doc: dict) -> Notification:
    """Convierte un documento MongoDB en el modelo publico contractual."""
    return Notification(
        id=doc["id"],
        alert_id=doc["alert_id"],
        timestamp=doc["timestamp"],
        metrics=doc.get("metrics", []),
    )


def _doc_to_mailbox_item(doc: dict) -> NotificationMailboxItem:
    """Convierte un documento MongoDB en la vista extendida del buzon."""
    return NotificationMailboxItem(
        id=doc["id"],
        alert_id=doc["alert_id"],
        user_id=doc["user_id"],
        timestamp=doc["timestamp"],
        subject=doc.get("subject", ""),
        metrics=doc.get("metrics", []),
        matches=[NotificationMatch(**match) for match in doc.get("matches", [])],
        delivery_channels=doc.get("delivery_channels", []),
        email_status=doc.get("email_status", "skipped"),
        email_sent_at=doc.get("email_sent_at"),
        email_error=doc.get("email_error"),
        read_at=doc.get("read_at"),
    )


def ensure_notification_for_alert(alert_id: int, notification_id: int) -> dict:
    """Comprueba que la notificacion exista y pertenezca a la alerta indicada."""
    notification = notifications_col.find_one(
        {"id": notification_id, "alert_id": alert_id},
        {"_id": 0},
    )
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notificacion no encontrada para la alerta",
        )
    return notification


def ensure_notification_for_user(user_id: int, notification_id: int) -> dict:
    """Comprueba que la notificacion exista y pertenezca al usuario indicado."""
    notification = notifications_col.find_one(
        {"id": notification_id, "user_id": user_id},
        {"_id": 0},
    )
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notificacion no encontrada para el usuario",
        )
    return notification


# ---------------------------------------------------------------------------
# Contract routes
# ---------------------------------------------------------------------------

@router.get(
    "/users/{user_id}/alerts/{alert_id}/notifications",
    response_model=List[Notification],
)
def list_alert_notifications(
    user_id: int,
    alert_id: int,
    current_user: UserInDB = Depends(get_current_user),
) -> List[Notification]:
    """Lista notificaciones de una alerta sin exponer campos internos."""
    ensure_user_can_access(user_id, current_user)
    ensure_alert_for_user(user_id, alert_id)
    cursor = notifications_col.find({"alert_id": alert_id}, {"_id": 0}).sort("timestamp", -1)
    return [_doc_to_notification(doc) for doc in cursor]


@router.post(
    "/users/{user_id}/alerts/{alert_id}/notifications",
    response_model=Notification,
    status_code=201,
)
def create_alert_notification(
    user_id: int,
    alert_id: int,
    payload: NotificationCreate,
    current_user: UserInDB = Depends(ensure_gestor_role),
) -> Notification:
    """Crea una notificacion contractual reutilizando la configuracion interna de la alerta."""
    ensure_user_can_access(user_id, current_user)
    alert = ensure_alert_for_user(user_id, alert_id)
    alert_doc = alerts_col.find_one(
        {"id": alert_id, "user_id": user_id},
        {"notification_channels": 1, "_id": 0},
    ) or {}
    delivery_channels = alert_doc.get("notification_channels") or ["app", "email"]
    now = datetime.now(timezone.utc)
    notification_id = next_mongo_id("notifications")
    notification_doc = {
        "id": notification_id,
        "alert_id": alert_id,
        "user_id": alert.user_id,
        **payload.model_dump(),
        "subject": (
            f"Actualizacion de {alert.name} en "
            f"{payload.timestamp.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
        ),
        "matches": [],
        "delivery_channels": delivery_channels,
        "email_status": "pending" if "email" in delivery_channels else "skipped",
        "email_sent_at": None,
        "email_error": None,
        "read_at": None,
        "created_at": now,
        "updated_at": now,
    }
    notifications_col.insert_one(notification_doc)
    return _doc_to_notification(notification_doc)


@router.get(
    "/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}",
    response_model=Notification,
)
def get_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    current_user: UserInDB = Depends(get_current_user),
) -> Notification:
    """Obtiene una notificacion contractual de una alerta concreta."""
    ensure_user_can_access(user_id, current_user)
    ensure_alert_for_user(user_id, alert_id)
    return _doc_to_notification(ensure_notification_for_alert(alert_id, notification_id))


@router.put(
    "/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}",
    response_model=Notification,
)
def update_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    payload: NotificationUpdate,
    current_user: UserInDB = Depends(ensure_gestor_role),
) -> Notification:
    """Actualiza una notificacion contractual existente."""
    ensure_user_can_access(user_id, current_user)
    ensure_alert_for_user(user_id, alert_id)
    ensure_notification_for_alert(alert_id, notification_id)
    update_data = payload.model_dump(exclude_unset=True)

    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        notifications_col.update_one(
            {"id": notification_id, "alert_id": alert_id},
            {"$set": update_data},
        )

    updated = notifications_col.find_one(
        {"id": notification_id, "alert_id": alert_id},
        {"_id": 0},
    )
    return _doc_to_notification(updated)


@router.delete(
    "/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
)
def delete_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    current_user: UserInDB = Depends(ensure_gestor_role),
) -> None:
    """Elimina una notificacion de una alerta."""
    ensure_user_can_access(user_id, current_user)
    ensure_alert_for_user(user_id, alert_id)
    ensure_notification_for_alert(alert_id, notification_id)
    notifications_col.delete_one({"id": notification_id, "alert_id": alert_id})


# ---------------------------------------------------------------------------
# Extension routes
# ---------------------------------------------------------------------------

@router.get(
    "/users/{user_id}/notifications",
    response_model=List[NotificationMailboxItem],
)
def list_user_notifications(
    user_id: int,
    current_user: UserInDB = Depends(get_current_user),
) -> List[NotificationMailboxItem]:
    """Lista el buzon interno del usuario filtrando el canal app."""
    ensure_user_can_access(user_id, current_user)
    cursor = notifications_col.find(
        {"user_id": user_id, "delivery_channels": "app"},
        {"_id": 0},
    ).sort("timestamp", -1)
    return [_doc_to_mailbox_item(doc) for doc in cursor]


@router.get(
    "/users/{user_id}/notifications/{notification_id}",
    response_model=NotificationMailboxItem,
)
def get_user_notification(
    user_id: int,
    notification_id: int,
    current_user: UserInDB = Depends(get_current_user),
) -> NotificationMailboxItem:
    """Obtiene una notificacion extendida del buzon del usuario."""
    ensure_user_can_access(user_id, current_user)
    return _doc_to_mailbox_item(ensure_notification_for_user(user_id, notification_id))


@router.patch(
    "/users/{user_id}/notifications/{notification_id}/read",
    response_model=NotificationReadState,
)
def mark_notification_read(
    user_id: int,
    notification_id: int,
    current_user: UserInDB = Depends(get_current_user),
) -> NotificationReadState:
    """Marca una notificacion del buzon como leida."""
    ensure_user_can_access(user_id, current_user)
    ensure_notification_for_user(user_id, notification_id)
    read_at = datetime.now(timezone.utc)
    notifications_col.update_one(
        {"id": notification_id, "user_id": user_id},
        {"$set": {"read_at": read_at, "updated_at": read_at}},
    )
    return NotificationReadState(id=notification_id, read_at=read_at)
