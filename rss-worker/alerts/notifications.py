from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_subject(alert_name: str, timestamp: datetime) -> str:
    when = timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
    return f"Actualizaci\u00f3n de {alert_name} en {when}"


def build_match(
    entry: dict,
    matched_descriptors: Iterable[str],
    *,
    source: str | None,
    category_id: int | None,
) -> dict:
    # Shape interno preparado para el futuro buzon y correo, sin cambiar la API publica.
    return {
        "rss_entry_id": entry.get("_id"),
        "rss_entry_hash": entry.get("hash_deduplicado"),
        "title": entry.get("titulo") or "",
        "link": entry.get("link") or "",
        "source": source,
        "published_at": entry.get("fecha_publicacion"),
        "summary": entry.get("resumen"),
        "matched_descriptors": list(matched_descriptors),
        "category_id": category_id,
    }


def build_notification_doc(
    *,
    notification_id: int,
    alert: dict,
    matches: list[dict],
    timestamp: datetime,
    descriptors_count: int,
) -> dict:
    delivery_channels = alert.get("notification_channels") or ["app"]
    # El envio real de email queda pendiente; el worker deja la notificacion en cola.
    email_status = "pending" if "email" in delivery_channels else "skipped"

    return {
        "id": notification_id,
        "alert_id": alert["id"],
        "user_id": alert["user_id"],
        "timestamp": timestamp,
        "subject": build_subject(alert.get("name", "alerta"), timestamp),
        "metrics": [
            {"name": "matches_count", "value": float(len(matches))},
            {"name": "descriptors_count", "value": float(descriptors_count)},
        ],
        "matches": matches,
        "delivery_channels": delivery_channels,
        "email_status": email_status,
        "email_sent_at": None,
        "email_error": None,
        "read_at": None,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def build_email_body(alert: dict, matches: list[dict], timestamp: datetime) -> str:
    """Construye el contenido textual del email a partir de la notificacion."""
    lines = [
        f"Actualizacion de {alert.get('name', 'alerta')}",
        f"Fecha de procesamiento: {timestamp.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Coincidencias detectadas: {len(matches)}",
        "",
    ]

    for index, match in enumerate(matches, start=1):
        lines.extend(
            [
                f"{index}. {match.get('title') or 'Sin titulo'}",
                f"Origen: {match.get('source') or 'desconocido'}",
                f"Fecha: {match.get('published_at') or 'desconocida'}",
                f"Resumen: {match.get('summary') or 'Sin resumen'}",
                f"Enlace: {match.get('link') or 'Sin enlace'}",
                "",
            ]
        )

    return "\n".join(lines).strip()
