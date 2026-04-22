from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..alertas.routes import ensure_alert_for_user
from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import next_mongo_id, notifications_col
from .models import Notification, NotificationCreate, NotificationUpdate

router = APIRouter(tags=["notifications"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _doc_to_notification(doc: dict) -> Notification:
    """Convierte un documento MongoDB en el modelo público de notificación."""
    return Notification(
        id=doc["id"],
        alert_id=doc["alert_id"],
        timestamp=doc["timestamp"],
        metrics=doc.get("metrics", []),
    )


def ensure_notification_for_alert(alert_id: int, notification_id: int) -> Notification:
    """Comprueba que la notificación exista y pertenezca a la alerta indicada."""
    notification = notifications_col.find_one(
        {"id": notification_id, "alert_id": alert_id},
        {"_id": 0},
    )
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notificación no encontrada para la alerta",
        )
    return _doc_to_notification(notification)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "/users/{user_id}/alerts/{alert_id}/notifications",
    response_model=List[Notification],
)
def list_alert_notifications(
    user_id: int,
    alert_id: int,
    _: UserInDB = Depends(get_current_user),
) -> List[Notification]:
    """Lista notificaciones de una alerta."""
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
    _: UserInDB = Depends(get_current_user),
) -> Notification:
    """Crea una notificación dentro de una alerta."""
    alert = ensure_alert_for_user(user_id, alert_id)
    now = datetime.now(timezone.utc)
    notification_id = next_mongo_id("notifications")
    notification_doc = {
        "id": notification_id,
        "alert_id": alert_id,
        "user_id": alert.user_id,
        **payload.model_dump(),
        "subject": f"Actualización de {alert.name}",
        "matches": [],
        "delivery_channels": ["app"],
        "email_status": "skipped",
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
    _: UserInDB = Depends(get_current_user),
) -> Notification:
    """Obtiene una notificación de una alerta concreta."""
    ensure_alert_for_user(user_id, alert_id)
    return ensure_notification_for_alert(alert_id, notification_id)


@router.put(
    "/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}",
    response_model=Notification,
)
def update_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    payload: NotificationUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Notification:
    """Actualiza una notificación existente."""
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
    _: UserInDB = Depends(get_current_user),
) -> None:
    """Elimina una notificación de una alerta."""
    ensure_alert_for_user(user_id, alert_id)
    ensure_notification_for_alert(alert_id, notification_id)
    notifications_col.delete_one({"id": notification_id, "alert_id": alert_id})
