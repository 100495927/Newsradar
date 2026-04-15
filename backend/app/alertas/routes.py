from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..dependencies import ensure_gestor_role, get_current_user
from ..auth.user import UserInDB
from ..store import alerts_store, next_id, notifications_store, users_col
from .models import Alert, AlertCreate, AlertUpdate

router = APIRouter(tags=["alerts"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_user_exists(user_id: int) -> None:
    """Lanza 404 si el usuario no existe."""
    if not users_col.find_one({"id": user_id}):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


def ensure_alert_for_user(user_id: int, alert_id: int) -> Alert:
    """Comprueba que la alerta exista y pertenezca al usuario indicado."""
    alert = alerts_store.get(alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    return alert


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}/alerts", response_model=List[Alert])
def list_user_alerts(user_id: int, _: UserInDB = Depends(get_current_user)) -> List[Alert]:
    """Lista alertas de un usuario concreto."""
    ensure_user_exists(user_id)
    return [a for a in alerts_store.values() if a.user_id == user_id]


@router.post(
    "/users/{user_id}/alerts",
    response_model=Alert,
    status_code=201,
    dependencies=[Depends(ensure_gestor_role)],
)
def create_user_alert(
    user_id: int,
    payload: AlertCreate,
    _: UserInDB = Depends(get_current_user),
) -> Alert:
    """Crea una alerta para un usuario (requiere rol gestor)."""
    ensure_user_exists(user_id)
    alert_id = next_id("alerts")
    alert = Alert(id=alert_id, user_id=user_id, **payload.model_dump())
    alerts_store[alert_id] = alert
    return alert


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
    alert = ensure_alert_for_user(user_id, alert_id)
    updated = alert.model_copy(update=payload.model_dump(exclude_unset=True))
    alerts_store[alert_id] = updated
    return updated


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
    notification_ids = [n.id for n in notifications_store.values() if n.alert_id == alert_id]
    for nid in notification_ids:
        notifications_store.pop(nid, None)
    alerts_store.pop(alert_id, None)
