from datetime import datetime, timezone

from alerts.notifications import build_match, build_notification_doc, build_subject


def test_build_subject_uses_required_format() -> None:
    timestamp = datetime(2026, 4, 19, 12, 30, tzinfo=timezone.utc)

    assert build_subject("Energia", timestamp) == "Actualizaci\u00f3n de Energia en 2026-04-19 12:30"


def test_build_notification_marks_email_pending() -> None:
    timestamp = datetime(2026, 4, 19, 12, 30, tzinfo=timezone.utc)
    alert = {
        "id": 5,
        "user_id": 2,
        "name": "Energia",
        "notification_channels": ["app", "email"],
    }
    match = {"title": "Noticia", "rss_entry_hash": "abc"}

    doc = build_notification_doc(
        notification_id=7,
        alert=alert,
        matches=[match],
        timestamp=timestamp,
        descriptors_count=3,
    )

    assert doc["email_status"] == "pending"
    assert doc["delivery_channels"] == ["app", "email"]
    assert doc["matches"] == [match]
    assert doc["metrics"] == [
        {"name": "matches_count", "value": 1.0},
        {"name": "descriptors_count", "value": 3.0},
    ]


def test_build_notification_marks_email_skipped_without_email_channel() -> None:
    timestamp = datetime(2026, 4, 19, 12, 30, tzinfo=timezone.utc)
    alert = {"id": 5, "user_id": 2, "name": "Energia", "notification_channels": ["app"]}

    doc = build_notification_doc(
        notification_id=7,
        alert=alert,
        matches=[],
        timestamp=timestamp,
        descriptors_count=1,
    )

    assert doc["email_status"] == "skipped"


def test_build_match_maps_rss_entry_fields() -> None:
    published_at = datetime(2026, 4, 19, 10, 0, tzinfo=timezone.utc)
    entry = {
        "_id": "entry-id",
        "hash_deduplicado": "hash-1",
        "titulo": "Titulo",
        "link": "https://example.test/news",
        "fecha_publicacion": published_at,
        "resumen": "Resumen",
    }

    match = build_match(
        entry,
        ["Titulo"],
        source="medio",
        category_id=4,
    )

    assert match == {
        "rss_entry_id": "entry-id",
        "rss_entry_hash": "hash-1",
        "title": "Titulo",
        "link": "https://example.test/news",
        "source": "medio",
        "published_at": published_at,
        "summary": "Resumen",
        "matched_descriptors": ["Titulo"],
        "category_id": 4,
    }
