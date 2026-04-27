from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from pymongo import ReturnDocument
from shared.utils import (
    floor_to_minute,
    next_run_after,
    next_run_on_or_after,
    send_notification_email_with_error,
)

from .matcher import clean_descriptors, find_matched_descriptors
from .notifications import build_email_body, build_match, build_notification_doc, utc_now

logger = logging.getLogger(__name__)


def process_alerts(db: Any, now: datetime | None = None) -> int:
    """Process active alerts after a RSS ingestion cycle.

    Returns the number of notification documents created.
    """
    app_db = db.db_app
    timestamp = now or utc_now()
    created_notifications = 0

    # Se procesa alerta a alerta para que un fallo puntual no rompa todo el ciclo RSS.
    for alert in app_db["alerts"].find({"enabled": True}):
        try:
            if _process_single_alert(app_db, alert, timestamp):
                created_notifications += 1
        except Exception:
            logger.exception("Fallo procesando alerta %s", alert.get("id"))

    if created_notifications:
        logger.info("Alertas procesadas. Notificaciones creadas: %s", created_notifications)
    else:
        logger.info("Alertas procesadas sin nuevas notificaciones")

    return created_notifications


def process_due_alerts(db: Any, now: datetime | None = None) -> int:
    """Process only alerts scheduled to run at the current minute."""
    app_db = db.db_app
    timestamp = floor_to_minute(now or utc_now())
    created_notifications = 0

    _initialize_unscheduled_alerts(app_db, timestamp)

    due_cursor = app_db["alerts"].find(
        {
            "enabled": True,
            "next_run_at": {"$lte": timestamp},
        }
    )
    for alert in due_cursor:
        try:
            next_run_at = _next_alert_run(alert, timestamp)
            if _process_single_alert(app_db, alert, timestamp, next_run_at):
                created_notifications += 1
        except Exception:
            logger.exception("Fallo procesando alerta programada %s", alert.get("id"))

    if created_notifications:
        logger.info(
            "Alertas programadas procesadas. Notificaciones creadas: %s",
            created_notifications,
        )
    else:
        logger.info("Alertas programadas procesadas sin nuevas notificaciones")

    return created_notifications


def deliver_pending_notifications(db: Any, now: datetime | None = None) -> int:
    """Intenta enviar por email las notificaciones que siguen pendientes."""
    app_db = db.db_app
    timestamp = now or utc_now()
    delivered = 0

    cursor = app_db["notifications"].find(
        {"email_status": "pending"},
        {"_id": 0},
    ).sort("created_at", 1)
    for notification_doc in cursor:
        try:
            alert = app_db["alerts"].find_one(
                {"id": notification_doc["alert_id"]},
                {"_id": 0},
            ) or {
                "id": notification_doc["alert_id"],
                "user_id": notification_doc["user_id"],
                "name": f"alerta {notification_doc['alert_id']}",
            }
            if _send_email_for_notification(app_db, alert, notification_doc, timestamp):
                delivered += 1
        except Exception:
            logger.exception(
                "Fallo entregando notificacion pendiente %s",
                notification_doc.get("id"),
            )

    if delivered:
        logger.info("Notificaciones pendientes enviadas por email: %s", delivered)
    else:
        logger.info("No habia notificaciones pendientes enviables por email")

    return delivered


def _process_single_alert(
    app_db: Any,
    alert: dict,
    timestamp: datetime,
    next_run_at: datetime | None = None,
) -> bool:
    descriptors = clean_descriptors(alert.get("descriptors"))
    # Si la alerta es nueva, empezamos a contar desde su creacion para no incluir historico previo.
    since = alert.get("last_checked_at") or alert.get("created_at") or timestamp

    matches: list[dict] = []
    source_cache: dict[Any, str | None] = {}
    cursor = app_db["rss_entradas"].find({"fecha_ingestion": {"$gt": since}}).sort(
        "fecha_ingestion", 1
    )

    if descriptors:
        for entry in cursor:
            matched_descriptors = find_matched_descriptors(entry, descriptors)
            if not matched_descriptors:
                continue
            # Deduplicacion por alerta + hash de entrada RSS para soportar reinicios del worker.
            if _entry_already_notified(app_db, alert["id"], entry.get("hash_deduplicado")):
                continue
            matches.append(
                build_match(
                    entry,
                    matched_descriptors,
                    source=_source_name(app_db, entry, source_cache),
                    category_id=alert.get("category_id"),
                )
            )

    created = False
    if matches:
        # Una notificacion por alerta y ciclo agrupa todas las noticias detectadas.
        notification_id = _next_sequence(app_db, "notifications", timestamp)
        notification_doc = build_notification_doc(
            notification_id=notification_id,
            alert=alert,
            matches=matches,
            timestamp=timestamp,
            descriptors_count=len(descriptors),
        )
        app_db["notifications"].insert_one(notification_doc)
        _deliver_notification(app_db, alert, notification_doc, timestamp)
        created = True

    _mark_alert_checked(app_db, alert["id"], timestamp, next_run_at)
    return created


def _initialize_unscheduled_alerts(app_db: Any, timestamp: datetime) -> None:
    unscheduled_cursor = app_db["alerts"].find(
        {
            "enabled": True,
            "$or": [
                {"next_run_at": None},
                {"next_run_at": {"$exists": False}},
            ],
        }
    )
    for alert in unscheduled_cursor:
        try:
            next_run = next_run_on_or_after(alert["cron_expression"], timestamp)
            app_db["alerts"].update_one(
                {"id": alert["id"]},
                {
                    "$set": {
                        "next_run_at": next_run,
                        "updated_at": timestamp,
                    }
                },
            )
        except Exception:
            logger.exception(
                "No se pudo inicializar next_run_at para alerta %s",
                alert.get("id"),
            )


def _next_alert_run(alert: dict, timestamp: datetime) -> datetime:
    return next_run_after(alert["cron_expression"], timestamp)


def _entry_already_notified(app_db: Any, alert_id: int, rss_entry_hash: str | None) -> bool:
    if not rss_entry_hash:
        return False
    return (
        app_db["notifications"].find_one(
            {"alert_id": alert_id, "matches.rss_entry_hash": rss_entry_hash},
            {"_id": 1},
        )
        is not None
    )


def _source_name(app_db: Any, entry: dict, source_cache: dict[Any, str | None]) -> str | None:
    source_id = entry.get("id_fuente")
    if source_id is None:
        return None
    # Cache local por ciclo para no consultar rss_fuentes repetidamente por cada noticia.
    if source_id not in source_cache:
        source = app_db["rss_fuentes"].find_one({"_id": source_id}, {"medio": 1, "rss": 1})
        source_cache[source_id] = None if not source else source.get("medio") or source.get("rss")
    return source_cache[source_id]


def _deliver_notification(
    app_db: Any,
    alert: dict,
    notification_doc: dict,
    timestamp: datetime,
) -> None:
    if "email" not in (notification_doc.get("delivery_channels") or []):
        return

    _send_email_for_notification(app_db, alert, notification_doc, timestamp)


def _send_email_for_notification(
    app_db: Any,
    alert: dict,
    notification_doc: dict,
    timestamp: datetime,
) -> bool:
    if "email" not in (notification_doc.get("delivery_channels") or []):
        return False

    user = app_db["users"].find_one({"id": alert["user_id"]}, {"email": 1, "_id": 0})
    email = None if not user else user.get("email")
    body = build_email_body(alert, notification_doc.get("matches", []), timestamp)
    sent, error = send_notification_email_with_error(
        email or "",
        notification_doc.get("subject", "Actualizacion de alerta"),
        body,
    )

    update_fields = {
        "updated_at": timestamp,
        "email_status": "sent" if sent else "failed",
        "email_error": error,
    }
    update_fields["email_sent_at"] = timestamp if sent else None
    app_db["notifications"].update_one(
        {"id": notification_doc["id"]},
        {"$set": update_fields},
    )
    return sent


def _next_sequence(app_db: Any, counter_name: str, timestamp: datetime) -> int:
    result = app_db["counters"].find_one_and_update(
        {"_id": counter_name},
        {
            "$inc": {"seq": 1},
            "$set": {"updated_at": timestamp},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(result["seq"])


def _mark_alert_checked(
    app_db: Any,
    alert_id: int,
    timestamp: datetime,
    next_run_at: datetime | None,
) -> None:
    update_fields = {
        "last_checked_at": timestamp,
        "last_run_at": timestamp,
        "updated_at": timestamp,
    }
    if next_run_at is not None:
        update_fields["next_run_at"] = next_run_at

    app_db["alerts"].update_one(
        {"id": alert_id},
        {"$set": update_fields},
    )
