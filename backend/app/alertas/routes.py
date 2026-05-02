from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from shared.utils import next_run_on_or_after, validate_minute_cron_expression

from ..dependencies import ensure_gestor_role, ensure_user_can_access, get_current_user
from ..auth.user import UserInDB
from shared.iptc_catalog import resolve_category
from ..store import alerts_col, next_mongo_id, notifications_col, users_col
from .models import (
    Alert,
    AlertCreate,
    AlertNotificationSettings,
    AlertNotificationSettingsUpdate,
    AlertUpdate,
)

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
        rss_channels_ids=doc.get("rss_channels_ids", []),
        information_sources_ids=doc.get("information_sources_ids", []),
        cron_expression=doc["cron_expression"],
        enabled=doc.get("enabled", True),
    )


def ensure_alert_for_user(user_id: int, alert_id: int) -> Alert:
    """Comprueba que la alerta exista y pertenezca al usuario indicado."""
    alert = alerts_col.find_one({"id": alert_id, "user_id": user_id}, {"_id": 0})
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    return _doc_to_alert(alert)


def _validate_cron_or_400(cron_expression: str) -> None:
    try:
        validate_minute_cron_expression(cron_expression)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _normalize_notification_channels(channels: list[str] | None) -> list[str]:
    normalized = list(dict.fromkeys(channels or ["app", "email"]))
    if not normalized:
        raise HTTPException(
            status_code=400,
            detail="La alerta debe tener al menos un canal de notificacion",
        )
    invalid = [channel for channel in normalized if channel not in {"app", "email"}]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Canales de notificacion no validos: {invalid}",
        )
    return normalized


def _resolve_alert_category_or_400(categories: list[dict] | None) -> tuple[int, list[dict[str, str]]]:
    if not categories:
        raise HTTPException(
            status_code=400,
            detail="La alerta debe incluir una categoría IPTC",
        )

    candidate = categories[0]
    if isinstance(candidate, dict):
        code = candidate.get("code")
        label = candidate.get("label")
    else:
        code = getattr(candidate, "code", None)
        label = getattr(candidate, "label", None)

    category = resolve_category(code) or resolve_category(label)
    if category is None:
        raise HTTPException(
            status_code=400,
            detail="La categoría de la alerta no corresponde a una categoría IPTC válida",
        )

    return category.id, [{"code": str(category.id), "label": category.name}]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}/alerts", response_model=List[Alert])
def list_user_alerts(user_id: int, _: UserInDB = Depends(get_current_user)) -> List[Alert]:
    """Lista alertas de un usuario concreto."""
    ensure_user_can_access(user_id, _)
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
    current_user: UserInDB = Depends(ensure_gestor_role),
) -> Alert:
    """Crea una alerta para un usuario autenticado."""
    ensure_user_can_access(user_id, current_user)
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
    _validate_cron_or_400(payload.cron_expression)
    category_id, normalized_categories = _resolve_alert_category_or_400(payload.categories)
    alert_id = next_mongo_id("alerts")
    alert_doc = {
        "id": alert_id,
        "user_id": user_id,
        **payload.model_dump(),
        "categories": normalized_categories,
        "category_id": category_id,
        "rss_channel_ids": [],
        "notification_channels": _normalize_notification_channels(["app", "email"]),
        "enabled": True,
        "last_checked_at": None,
        "last_run_at": None,
        "next_run_at": next_run_on_or_after(payload.cron_expression, now),
        "created_at": now,
        "updated_at": now,
    }
    alerts_col.insert_one(alert_doc)
    return _doc_to_alert(alert_doc)


@router.get("/users/{user_id}/alerts/{alert_id}", response_model=Alert)
def get_user_alert(
    user_id: int,
    alert_id: int,
    current_user: UserInDB = Depends(get_current_user),
) -> Alert:
    """Recupera una alerta concreta de un usuario."""
    ensure_user_can_access(user_id, current_user)
    return ensure_alert_for_user(user_id, alert_id)


@router.put("/users/{user_id}/alerts/{alert_id}", response_model=Alert)
def update_user_alert(
    user_id: int,
    alert_id: int,
    payload: AlertUpdate,
    current_user: UserInDB = Depends(ensure_gestor_role),
) -> Alert:
    """Actualiza una alerta de usuario."""
    ensure_user_can_access(user_id, current_user)
    ensure_alert_for_user(user_id, alert_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "descriptors" in update_data and not update_data["descriptors"]:
        raise HTTPException(
            status_code=400,
            detail="La alerta debe incluir al menos un descriptor",
        )

    now = datetime.now(timezone.utc)

    if "cron_expression" in update_data:
        _validate_cron_or_400(update_data["cron_expression"])
        update_data["next_run_at"] = next_run_on_or_after(update_data["cron_expression"], now)

    if "categories" in update_data:
        category_id, normalized_categories = _resolve_alert_category_or_400(update_data["categories"])
        update_data["categories"] = normalized_categories
        update_data["category_id"] = category_id

    if update_data.get("enabled") is False:
        update_data["next_run_at"] = None

    if update_data.get("enabled") is True and "next_run_at" not in update_data:
        current = alerts_col.find_one(
            {"id": alert_id, "user_id": user_id},
            {"cron_expression": 1, "next_run_at": 1, "_id": 0},
        )
        if current and current.get("next_run_at") is None:
            update_data["next_run_at"] = next_run_on_or_after(current["cron_expression"], now)

    if update_data:
        update_data["updated_at"] = now
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
    current_user: UserInDB = Depends(ensure_gestor_role),
) -> None:
    """Elimina una alerta y sus notificaciones vinculadas."""
    ensure_user_can_access(user_id, current_user)
    ensure_alert_for_user(user_id, alert_id)
    notifications_col.delete_many({"alert_id": alert_id})
    alerts_col.delete_one({"id": alert_id, "user_id": user_id})


@router.get(
    "/users/{user_id}/alerts/{alert_id}/notification-settings",
    response_model=AlertNotificationSettings,
)
def get_alert_notification_settings(
    user_id: int,
    alert_id: int,
    current_user: UserInDB = Depends(ensure_gestor_role),
) -> AlertNotificationSettings:
    """Devuelve la configuracion interna de canales de notificacion de una alerta."""
    ensure_user_can_access(user_id, current_user)
    ensure_alert_for_user(user_id, alert_id)
    alert = alerts_col.find_one(
        {"id": alert_id, "user_id": user_id},
        {"notification_channels": 1, "_id": 0},
    )
    return AlertNotificationSettings(
        channels=_normalize_notification_channels(alert.get("notification_channels")),
    )


@router.put(
    "/users/{user_id}/alerts/{alert_id}/notification-settings",
    response_model=AlertNotificationSettings,
)
def update_alert_notification_settings(
    user_id: int,
    alert_id: int,
    payload: AlertNotificationSettingsUpdate,
    current_user: UserInDB = Depends(ensure_gestor_role),
) -> AlertNotificationSettings:
    """Actualiza la configuracion de entrega app/email sin alterar el contrato publico de Alert."""
    ensure_user_can_access(user_id, current_user)
    ensure_alert_for_user(user_id, alert_id)
    channels = _normalize_notification_channels(payload.channels)
    alerts_col.update_one(
        {"id": alert_id, "user_id": user_id},
        {
            "$set": {
                "notification_channels": channels,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return AlertNotificationSettings(channels=channels)
