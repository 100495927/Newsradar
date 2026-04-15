from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..alertas.routes import ensure_alert_for_user
from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import next_id, notifications_store
from .models import Notification, NotificationCreate, NotificationUpdate

router = APIRouter(tags=["notifications"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_notification_for_alert(alert_id: int, notification_id: int) -> Notification:
    """Comprueba que la notificación exista y pertenezca a la alerta indicada."""
    notification = notifications_store.get(notification_id)
    if not notification or notification.alert_id != alert_id:
        raise HTTPException(
            status_code=404,
            detail="Notificación no encontrada para la alerta",
        )
    return notification


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
    return [n for n in notifications_store.values() if n.alert_id == alert_id]


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
    ensure_alert_for_user(user_id, alert_id)
    notification_id = next_id("notifications")
    notification = Notification(id=notification_id, alert_id=alert_id, **payload.model_dump())
    notifications_store[notification_id] = notification
    return notification


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
    notification = ensure_notification_for_alert(alert_id, notification_id)
    updated = notification.model_copy(update=payload.model_dump(exclude_unset=True))
    notifications_store[notification_id] = updated
    return updated


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
    notifications_store.pop(notification_id, None)
