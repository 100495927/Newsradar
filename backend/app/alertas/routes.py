from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from shared.utils import next_run_after, next_run_on_or_after, validate_minute_cron_expression

from ..dependencies import ensure_gestor_role, ensure_user_can_access, get_current_user
from ..auth.user import UserInDB
from shared.iptc_catalog import resolve_category
from ..store import (
    alerts_col,
    information_sources_col,
    next_mongo_id,
    notifications_col,
    rss_channels_col,
    users_col,
)
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
        rss_channels_ids=[str(value) for value in doc.get("rss_channel_ids", [])],
        information_sources_ids=[
            str(value) for value in doc.get("information_sources_ids", [])
        ],
        cron_expression=doc["cron_expression"],
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
            detail="La alerta debe incluir exactamente una categoría IPTC",
        )
    if len(categories) != 1:
        raise HTTPException(
            status_code=400,
            detail="La alerta debe incluir exactamente una categoría IPTC",
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


def _normalize_resource_ids(raw_ids: list[str] | None, field_name: str) -> list[int]:
    if not raw_ids:
        return []

    normalized: list[int] = []
    seen: set[int] = set()
    for raw_value in raw_ids:
        if isinstance(raw_value, int):
            parsed = raw_value
        elif isinstance(raw_value, str) and raw_value.isdigit():
            parsed = int(raw_value)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} debe contener IDs enteros serializados como string",
            )
        if parsed not in seen:
            normalized.append(parsed)
            seen.add(parsed)
    return normalized


def _validate_alert_scope_or_400(
    category_id: int,
    rss_channel_ids: list[int],
    information_source_ids: list[int],
) -> tuple[list[int], list[int]]:
    normalized_channel_ids = list(dict.fromkeys(rss_channel_ids))
    normalized_source_ids = list(dict.fromkeys(information_source_ids))

    if normalized_channel_ids:
        channel_docs = list(
            rss_channels_col.find(
                {
                    "id": {"$in": normalized_channel_ids},
                    "deleted_at": {"$exists": False},
                },
                {"id": 1, "category_id": 1, "information_source_id": 1, "_id": 0},
            )
        )
        found_channel_ids = {int(doc["id"]) for doc in channel_docs}
        missing_channels = [
            channel_id
            for channel_id in normalized_channel_ids
            if channel_id not in found_channel_ids
        ]
        if missing_channels:
            raise HTTPException(
                status_code=400,
                detail=f"Canales RSS no encontrados: {missing_channels}",
            )
        incompatible_channels = [
            int(doc["id"]) for doc in channel_docs if int(doc["category_id"]) != category_id
        ]
        if incompatible_channels:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Los canales RSS seleccionados no son compatibles con la categoria "
                    f"de la alerta: {incompatible_channels}"
                ),
            )
        if normalized_source_ids:
            channels_outside_selected_sources = [
                int(doc["id"])
                for doc in channel_docs
                if int(doc["information_source_id"]) not in normalized_source_ids
            ]
            if channels_outside_selected_sources:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Los canales RSS seleccionados no pertenecen a las fuentes "
                        f"indicadas: {channels_outside_selected_sources}"
                    ),
                )

    if normalized_source_ids:
        source_docs = list(
            information_sources_col.find(
                {
                    "id": {"$in": normalized_source_ids},
                    "deleted_at": {"$exists": False},
                },
                {"id": 1, "_id": 0},
            )
        )
        found_source_ids = {int(doc["id"]) for doc in source_docs}
        missing_sources = [
            source_id
            for source_id in normalized_source_ids
            if source_id not in found_source_ids
        ]
        if missing_sources:
            raise HTTPException(
                status_code=400,
                detail=f"Fuentes de informacion no encontradas: {missing_sources}",
            )

        compatible_source_ids = {
            int(doc["information_source_id"])
            for doc in rss_channels_col.find(
                {
                    "information_source_id": {"$in": normalized_source_ids},
                    "category_id": category_id,
                    "deleted_at": {"$exists": False},
                },
                {"information_source_id": 1, "_id": 0},
            )
        }
        incompatible_sources = [
            source_id
            for source_id in normalized_source_ids
            if source_id not in compatible_source_ids
        ]
        if incompatible_sources:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Las fuentes seleccionadas no tienen canales RSS compatibles con la "
                    f"categoria de la alerta: {incompatible_sources}"
                ),
            )

    return normalized_channel_ids, normalized_source_ids


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
    normalized_channel_ids, normalized_source_ids = _validate_alert_scope_or_400(
        category_id,
        _normalize_resource_ids(payload.rss_channels_ids, "rss_channels_ids"),
        _normalize_resource_ids(
            payload.information_sources_ids,
            "information_sources_ids",
        ),
    )
    payload_data = payload.model_dump()
    payload_data.pop("rss_channels_ids", None)
    payload_data.pop("information_sources_ids", None)
    alert_id = next_mongo_id("alerts")
    alert_doc = {
        "id": alert_id,
        "user_id": user_id,
        **payload_data,
        "categories": normalized_categories,
        "category_id": category_id,
        "rss_channel_ids": normalized_channel_ids,
        "information_sources_ids": normalized_source_ids,
        "notification_channels": _normalize_notification_channels(["app", "email"]),
        "enabled": True,
        "last_checked_at": None,
        "last_run_at": None,
        "next_run_at": next_run_after(payload.cron_expression, now),
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
        update_data["next_run_at"] = next_run_after(update_data["cron_expression"], now)

    if "categories" in update_data:
        category_id, normalized_categories = _resolve_alert_category_or_400(update_data["categories"])
        update_data["categories"] = normalized_categories
        update_data["category_id"] = category_id

    current_doc = alerts_col.find_one({"id": alert_id, "user_id": user_id}, {"_id": 0})
    if current_doc is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")

    if (
        "rss_channels_ids" in update_data
        or "information_sources_ids" in update_data
        or "category_id" in update_data
    ):
        effective_category_id = int(update_data.get("category_id", current_doc["category_id"]))
        normalized_channel_ids, normalized_source_ids = _validate_alert_scope_or_400(
            effective_category_id,
            _normalize_resource_ids(
                update_data.get(
                    "rss_channels_ids",
                    [str(value) for value in current_doc.get("rss_channel_ids", [])],
                ),
                "rss_channels_ids",
            ),
            _normalize_resource_ids(
                update_data.get(
                    "information_sources_ids",
                    [
                        str(value)
                        for value in current_doc.get("information_sources_ids", [])
                    ],
                ),
                "information_sources_ids",
            ),
        )
        update_data["rss_channel_ids"] = normalized_channel_ids
        update_data["information_sources_ids"] = normalized_source_ids
        update_data.pop("rss_channels_ids", None)
        update_data.pop("information_sources_ids", None)

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
