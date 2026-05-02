from __future__ import annotations

from datetime import datetime, timedelta, timezone

from alerts.processor import deliver_pending_notifications, process_alerts, process_due_alerts


class FakeCursor(list):
    def sort(self, key: str, direction: int):
        return FakeCursor(sorted(self, key=lambda doc: doc.get(key), reverse=direction < 0))


class FakeCollection:
    def __init__(self, docs: list[dict] | None = None):
        self.docs = docs or []

    def find(self, query: dict | None = None, projection: dict | None = None):
        return FakeCursor([doc for doc in self.docs if _matches(doc, query or {})])

    def find_one(self, query: dict | None = None, projection: dict | None = None):
        for doc in self.find(query, projection):
            return doc
        return None

    def insert_one(self, doc: dict):
        self.docs.append(doc)
        return type("InsertResult", (), {"inserted_id": doc.get("_id")})()

    def update_one(self, query: dict, update: dict, upsert: bool = False):
        for doc in self.docs:
            if _matches(doc, query):
                doc.update(update.get("$set", {}))
                return type("UpdateResult", (), {"modified_count": 1})()
        if upsert:
            doc = dict(query)
            doc.update(update.get("$setOnInsert", {}))
            doc.update(update.get("$set", {}))
            self.docs.append(doc)
        return type("UpdateResult", (), {"modified_count": 0})()

    def find_one_and_update(
        self,
        query: dict,
        update: dict,
        upsert: bool = False,
        return_document=None,
    ):
        doc = self.find_one(query)
        if doc is None and upsert:
            doc = dict(query)
            doc["seq"] = 0
            self.docs.append(doc)
        if doc is None:
            return None
        for key, value in update.get("$inc", {}).items():
            doc[key] = doc.get(key, 0) + value
        doc.update(update.get("$set", {}))
        return doc


class FakeAppDb:
    def __init__(self, collections: dict[str, FakeCollection]):
        self.collections = collections

    def __getitem__(self, name: str) -> FakeCollection:
        return self.collections[name]


class FakeDb:
    def __init__(self, app_db: FakeAppDb):
        self.db_app = app_db


def test_process_alerts_creates_grouped_notification_and_avoids_duplicates(monkeypatch) -> None:
    now = datetime(2026, 4, 19, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(
        "alerts.processor.send_notification_email_with_error",
        lambda to_email, subject, body: (True, None),
    )
    app_db = FakeAppDb(
        {
            "alerts": FakeCollection(
                [
                    {
                        "id": 10,
                        "user_id": 3,
                        "name": "Energia",
                        "descriptors": ["energia"],
                        "category_id": 8,
                        "notification_channels": ["app", "email"],
                        "enabled": True,
                        "last_checked_at": None,
                        "created_at": now - timedelta(hours=3),
                    }
                ]
            ),
            "rss_entradas": FakeCollection(
                [
                    {
                        "_id": "entry-1",
                        "information_source_id": 1,
                        "rss_channel_id": 101,
                        "source_name": "medio-test",
                        "category_id": 8,
                        "titulo": "Nueva crisis de energia",
                        "resumen": "Resumen",
                        "link": "https://example.test/1",
                        "hash_deduplicado": "hash-1",
                        "fecha_publicacion": now - timedelta(hours=2),
                        "fecha_ingestion": now - timedelta(hours=1),
                    }
                ]
            ),
            "information_sources": FakeCollection([{"id": 1, "name": "medio-test"}]),
            "users": FakeCollection([{"id": 3, "email": "manager@example.test"}]),
            "notifications": FakeCollection([]),
            "counters": FakeCollection([{"_id": "notifications", "seq": 0}]),
        }
    )

    created = process_alerts(FakeDb(app_db), now)
    created_again = process_alerts(FakeDb(app_db), now)

    assert created == 1
    assert created_again == 0
    assert len(app_db["notifications"].docs) == 1
    notification = app_db["notifications"].docs[0]
    assert notification["id"] == 1
    assert notification["alert_id"] == 10
    assert notification["email_status"] == "sent"
    assert notification["email_sent_at"] == now
    assert notification["matches"][0]["rss_entry_hash"] == "hash-1"
    assert notification["matches"][0]["source"] == "medio-test"
    assert app_db["alerts"].docs[0]["last_checked_at"] == now


def test_process_alerts_without_matches_updates_alert_but_creates_no_notification() -> None:
    now = datetime(2026, 4, 19, 12, 0, tzinfo=timezone.utc)
    app_db = FakeAppDb(
        {
            "alerts": FakeCollection(
                [
                    {
                        "id": 10,
                        "user_id": 3,
                        "name": "Energia",
                        "descriptors": ["energia"],
                        "category_id": 8,
                        "notification_channels": ["app"],
                        "enabled": True,
                        "last_checked_at": None,
                        "created_at": now - timedelta(hours=3),
                    }
                ]
            ),
            "rss_entradas": FakeCollection(
                [
                    {
                        "titulo": "Deportes",
                        "category_id": 7,
                        "resumen": "Resultado",
                        "hash_deduplicado": "hash-1",
                        "fecha_ingestion": now - timedelta(hours=1),
                    }
                ]
            ),
            "information_sources": FakeCollection([]),
            "users": FakeCollection([{"id": 3, "email": "manager@example.test"}]),
            "notifications": FakeCollection([]),
            "counters": FakeCollection([{"_id": "notifications", "seq": 0}]),
        }
    )

    created = process_alerts(FakeDb(app_db), now)

    assert created == 0
    assert app_db["notifications"].docs == []
    assert app_db["alerts"].docs[0]["last_run_at"] == now


def test_process_alerts_new_alert_only_matches_entries_after_created_at() -> None:
    now = datetime(2026, 4, 19, 12, 0, tzinfo=timezone.utc)
    created_at = now - timedelta(minutes=30)
    app_db = FakeAppDb(
        {
            "alerts": FakeCollection(
                [
                    {
                        "id": 10,
                        "user_id": 3,
                        "name": "Energia",
                        "descriptors": ["energia"],
                        "category_id": 8,
                        "notification_channels": ["app"],
                        "enabled": True,
                        "last_checked_at": None,
                        "created_at": created_at,
                    }
                ]
            ),
            "rss_entradas": FakeCollection(
                [
                    {
                        "_id": "entry-old",
                        "information_source_id": 1,
                        "rss_channel_id": 101,
                        "source_name": "medio-test",
                        "category_id": 8,
                        "titulo": "Crisis de energia de ayer",
                        "resumen": "Resumen",
                        "link": "https://example.test/old",
                        "hash_deduplicado": "hash-old",
                        "fecha_publicacion": now - timedelta(hours=3),
                        "fecha_ingestion": now - timedelta(hours=2),
                    },
                    {
                        "_id": "entry-new",
                        "information_source_id": 1,
                        "rss_channel_id": 101,
                        "source_name": "medio-test",
                        "category_id": 8,
                        "titulo": "Nueva crisis de energia",
                        "resumen": "Resumen",
                        "link": "https://example.test/new",
                        "hash_deduplicado": "hash-new",
                        "fecha_publicacion": now - timedelta(minutes=20),
                        "fecha_ingestion": now - timedelta(minutes=10),
                    },
                ]
            ),
            "information_sources": FakeCollection([{"id": 1, "name": "medio-test"}]),
            "users": FakeCollection([{"id": 3, "email": "manager@example.test"}]),
            "notifications": FakeCollection([]),
            "counters": FakeCollection([{"_id": "notifications", "seq": 0}]),
        }
    )

    created = process_alerts(FakeDb(app_db), now)

    assert created == 1
    assert len(app_db["notifications"].docs) == 1
    notification = app_db["notifications"].docs[0]
    assert len(notification["matches"]) == 1
    assert notification["matches"][0]["rss_entry_hash"] == "hash-new"


def test_process_due_alerts_only_runs_due_alerts_and_sets_next_run() -> None:
    now = datetime(2026, 4, 19, 12, 0, tzinfo=timezone.utc)
    app_db = FakeAppDb(
        {
            "alerts": FakeCollection(
                [
                    {
                        "id": 10,
                        "user_id": 3,
                        "name": "Energia",
                        "descriptors": ["energia"],
                        "category_id": 8,
                        "notification_channels": ["app"],
                        "cron_expression": "*/5 * * * *",
                        "enabled": True,
                        "last_checked_at": None,
                        "next_run_at": now,
                        "created_at": now - timedelta(hours=1),
                    },
                    {
                        "id": 11,
                        "user_id": 3,
                        "name": "No due",
                        "descriptors": ["energia"],
                        "category_id": 8,
                        "notification_channels": ["app"],
                        "cron_expression": "*/5 * * * *",
                        "enabled": True,
                        "last_checked_at": None,
                        "next_run_at": now + timedelta(minutes=5),
                        "created_at": now - timedelta(hours=1),
                    },
                ]
            ),
            "rss_entradas": FakeCollection(
                [
                    {
                        "_id": "entry-1",
                        "information_source_id": 1,
                        "rss_channel_id": 101,
                        "source_name": "medio-test",
                        "category_id": 8,
                        "titulo": "Nueva crisis de energia",
                        "resumen": "Resumen",
                        "link": "https://example.test/1",
                        "hash_deduplicado": "hash-1",
                        "fecha_publicacion": now - timedelta(minutes=10),
                        "fecha_ingestion": now - timedelta(minutes=5),
                    }
                ]
            ),
            "information_sources": FakeCollection([{"id": 1, "name": "medio-test"}]),
            "users": FakeCollection([{"id": 3, "email": "manager@example.test"}]),
            "notifications": FakeCollection([]),
            "counters": FakeCollection([{"_id": "notifications", "seq": 0}]),
        }
    )

    created = process_due_alerts(FakeDb(app_db), now)

    assert created == 1
    assert len(app_db["notifications"].docs) == 1
    assert app_db["alerts"].docs[0]["last_run_at"] == now
    assert app_db["alerts"].docs[0]["next_run_at"] == now + timedelta(minutes=5)
    assert app_db["alerts"].docs[1].get("last_run_at") is None


def test_process_alerts_filters_entries_by_selected_source_and_channel() -> None:
    now = datetime(2026, 4, 19, 12, 0, tzinfo=timezone.utc)
    app_db = FakeAppDb(
        {
            "alerts": FakeCollection(
                [
                    {
                        "id": 10,
                        "user_id": 3,
                        "name": "Energia",
                        "descriptors": ["energia"],
                        "category_id": 8,
                        "rss_channel_ids": [101],
                        "information_sources_ids": [1],
                        "notification_channels": ["app"],
                        "enabled": True,
                        "last_checked_at": None,
                        "created_at": now - timedelta(hours=3),
                    }
                ]
            ),
            "rss_entradas": FakeCollection(
                [
                    {
                        "_id": "entry-match",
                        "information_source_id": 1,
                        "rss_channel_id": 101,
                        "source_name": "medio-test",
                        "category_id": 8,
                        "titulo": "Nueva crisis de energia",
                        "resumen": "Resumen",
                        "link": "https://example.test/1",
                        "hash_deduplicado": "hash-1",
                        "fecha_publicacion": now - timedelta(hours=2),
                        "fecha_ingestion": now - timedelta(hours=1),
                    },
                    {
                        "_id": "entry-other-channel",
                        "information_source_id": 1,
                        "rss_channel_id": 999,
                        "source_name": "medio-test",
                        "category_id": 8,
                        "titulo": "Nueva crisis de energia",
                        "resumen": "Resumen",
                        "link": "https://example.test/2",
                        "hash_deduplicado": "hash-2",
                        "fecha_publicacion": now - timedelta(hours=2),
                        "fecha_ingestion": now - timedelta(hours=1),
                    },
                ]
            ),
            "information_sources": FakeCollection([{"id": 1, "name": "medio-test"}]),
            "users": FakeCollection([{"id": 3, "email": "manager@example.test"}]),
            "notifications": FakeCollection([]),
            "counters": FakeCollection([{"_id": "notifications", "seq": 0}]),
        }
    )

    created = process_alerts(FakeDb(app_db), now)

    assert created == 1
    notification = app_db["notifications"].docs[0]
    assert len(notification["matches"]) == 1
    assert notification["matches"][0]["rss_entry_hash"] == "hash-1"


def test_process_alerts_filters_entries_by_alert_category() -> None:
    now = datetime(2026, 4, 19, 12, 0, tzinfo=timezone.utc)
    app_db = FakeAppDb(
        {
            "alerts": FakeCollection(
                [
                    {
                        "id": 10,
                        "user_id": 3,
                        "name": "Energia",
                        "descriptors": ["energia"],
                        "category_id": 8,
                        "notification_channels": ["app"],
                        "enabled": True,
                        "last_checked_at": None,
                        "created_at": now - timedelta(hours=3),
                    }
                ]
            ),
            "rss_entradas": FakeCollection(
                [
                    {
                        "_id": "entry-1",
                        "information_source_id": 1,
                        "rss_channel_id": 101,
                        "source_name": "medio-test",
                        "category_id": 7,
                        "titulo": "Nueva crisis de energia",
                        "resumen": "Resumen",
                        "link": "https://example.test/1",
                        "hash_deduplicado": "hash-1",
                        "fecha_publicacion": now - timedelta(hours=2),
                        "fecha_ingestion": now - timedelta(hours=1),
                    }
                ]
            ),
            "information_sources": FakeCollection([{"id": 1, "name": "medio-test"}]),
            "users": FakeCollection([{"id": 3, "email": "manager@example.test"}]),
            "notifications": FakeCollection([]),
            "counters": FakeCollection([{"_id": "notifications", "seq": 0}]),
        }
    )

    created = process_alerts(FakeDb(app_db), now)

    assert created == 0
    assert app_db["notifications"].docs == []


def test_process_due_alerts_initializes_missing_next_run_without_running() -> None:
    now = datetime(2026, 4, 19, 12, 3, tzinfo=timezone.utc)
    app_db = FakeAppDb(
        {
            "alerts": FakeCollection(
                [
                    {
                        "id": 10,
                        "user_id": 3,
                        "name": "Energia",
                        "descriptors": ["energia"],
                        "category_id": 8,
                        "notification_channels": ["app"],
                        "cron_expression": "*/5 * * * *",
                        "enabled": True,
                        "last_checked_at": None,
                        "next_run_at": None,
                        "created_at": now - timedelta(hours=1),
                    }
                ]
            ),
            "rss_entradas": FakeCollection([]),
            "information_sources": FakeCollection([]),
            "users": FakeCollection([{"id": 3, "email": "manager@example.test"}]),
            "notifications": FakeCollection([]),
            "counters": FakeCollection([{"_id": "notifications", "seq": 0}]),
        }
    )

    created = process_due_alerts(FakeDb(app_db), now)

    assert created == 0
    assert app_db["notifications"].docs == []
    assert app_db["alerts"].docs[0]["next_run_at"] == datetime(
        2026, 4, 19, 12, 5, tzinfo=timezone.utc
    )
    assert app_db["alerts"].docs[0].get("last_run_at") is None


def test_deliver_pending_notifications_updates_email_status(monkeypatch) -> None:
    now = datetime(2026, 4, 19, 12, 15, tzinfo=timezone.utc)
    monkeypatch.setattr(
        "alerts.processor.send_notification_email_with_error",
        lambda to_email, subject, body: (True, None),
    )
    app_db = FakeAppDb(
        {
            "alerts": FakeCollection(
                [
                    {
                        "id": 10,
                        "user_id": 3,
                        "name": "Energia",
                        "notification_channels": ["app", "email"],
                    }
                ]
            ),
            "users": FakeCollection([{"id": 3, "email": "manager@example.test"}]),
            "notifications": FakeCollection(
                [
                    {
                        "id": 7,
                        "alert_id": 10,
                        "user_id": 3,
                        "timestamp": now - timedelta(minutes=2),
                        "subject": "Actualizacion de Energia",
                        "metrics": [],
                        "matches": [
                            {
                                "title": "Titulo",
                                "link": "https://example.test/1",
                                "source": "medio-test",
                                "published_at": now - timedelta(minutes=3),
                                "summary": "Resumen",
                                "matched_descriptors": ["energia"],
                            }
                        ],
                        "delivery_channels": ["app", "email"],
                        "email_status": "pending",
                        "email_sent_at": None,
                        "email_error": None,
                        "read_at": None,
                        "created_at": now - timedelta(minutes=2),
                        "updated_at": now - timedelta(minutes=2),
                    }
                ]
            ),
            "rss_entradas": FakeCollection([]),
            "information_sources": FakeCollection([]),
            "counters": FakeCollection([{"_id": "notifications", "seq": 7}]),
        }
    )

    delivered = deliver_pending_notifications(FakeDb(app_db), now)

    assert delivered == 1
    notification = app_db["notifications"].docs[0]
    assert notification["email_status"] == "sent"
    assert notification["email_sent_at"] == now


def _matches(doc: dict, query: dict) -> bool:
    or_conditions = query.get("$or")
    if or_conditions:
        if not any(_matches(doc, condition) for condition in or_conditions):
            return False

    for key, expected in query.items():
        if key == "$or":
            continue
        actual = _get_value(doc, key)
        if isinstance(expected, dict):
            if "$gt" in expected:
                if not actual or actual <= expected["$gt"]:
                    return False
            if "$lte" in expected:
                if actual is None or actual > expected["$lte"]:
                    return False
            if "$in" in expected:
                if actual not in expected["$in"]:
                    return False
            if "$exists" in expected:
                exists = actual is not None
                if exists != expected["$exists"]:
                    return False
        elif actual != expected:
            return False
    return True


def _get_value(doc: dict, dotted_key: str):
    current = doc
    for part in dotted_key.split("."):
        if isinstance(current, list):
            return [_get_value(item, part) for item in current]
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current
