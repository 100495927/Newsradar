from __future__ import annotations

from datetime import datetime, timedelta, timezone

from alerts.processor import process_alerts


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


def test_process_alerts_creates_grouped_notification_and_avoids_duplicates() -> None:
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
                        "id_fuente": "source-1",
                        "titulo": "Nueva crisis de energia",
                        "resumen": "Resumen",
                        "link": "https://example.test/1",
                        "hash_deduplicado": "hash-1",
                        "fecha_publicacion": now - timedelta(hours=2),
                        "fecha_ingestion": now - timedelta(hours=1),
                    }
                ]
            ),
            "rss_fuentes": FakeCollection([{"_id": "source-1", "medio": "medio-test"}]),
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
    assert notification["email_status"] == "pending"
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
                        "resumen": "Resultado",
                        "hash_deduplicado": "hash-1",
                        "fecha_ingestion": now - timedelta(hours=1),
                    }
                ]
            ),
            "rss_fuentes": FakeCollection([]),
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
                        "id_fuente": "source-1",
                        "titulo": "Crisis de energia de ayer",
                        "resumen": "Resumen",
                        "link": "https://example.test/old",
                        "hash_deduplicado": "hash-old",
                        "fecha_publicacion": now - timedelta(hours=3),
                        "fecha_ingestion": now - timedelta(hours=2),
                    },
                    {
                        "_id": "entry-new",
                        "id_fuente": "source-1",
                        "titulo": "Nueva crisis de energia",
                        "resumen": "Resumen",
                        "link": "https://example.test/new",
                        "hash_deduplicado": "hash-new",
                        "fecha_publicacion": now - timedelta(minutes=20),
                        "fecha_ingestion": now - timedelta(minutes=10),
                    },
                ]
            ),
            "rss_fuentes": FakeCollection([{"_id": "source-1", "medio": "medio-test"}]),
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


def _matches(doc: dict, query: dict) -> bool:
    for key, expected in query.items():
        actual = _get_value(doc, key)
        if isinstance(expected, dict) and "$gt" in expected:
            if not actual or actual <= expected["$gt"]:
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
