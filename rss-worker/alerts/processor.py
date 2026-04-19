from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import ReturnDocument

from .matcher import clean_descriptors, find_matched_descriptors
from .notifications import build_match, build_notification_doc, utc_now

logger = logging.getLogger(__name__)

INITIAL_LOOKBACK_HOURS = 24


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


def _process_single_alert(app_db: Any, alert: dict, timestamp: datetime) -> bool:
    descriptors = clean_descriptors(alert.get("descriptors"))
    # Si la alerta es nueva, limitamos la primera busqueda para evitar re-notificar todo el historico.
    since = alert.get("last_checked_at") or timestamp - timedelta(hours=INITIAL_LOOKBACK_HOURS)

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
        app_db["notifications"].insert_one(
            build_notification_doc(
                notification_id=notification_id,
                alert=alert,
                matches=matches,
                timestamp=timestamp,
                descriptors_count=len(descriptors),
            )
        )
        created = True

    _mark_alert_checked(app_db, alert["id"], timestamp)
    return created


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


def _mark_alert_checked(app_db: Any, alert_id: int, timestamp: datetime) -> None:
    app_db["alerts"].update_one(
        {"id": alert_id},
        {
            "$set": {
                "last_checked_at": timestamp,
                "last_run_at": timestamp,
                "updated_at": timestamp,
            }
        },
    )
