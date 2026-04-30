from __future__ import annotations

from datetime import datetime, timezone

from app.alertas.models import AlertNotificationSettingsUpdate
from app.alertas import routes as alert_routes
from app.auth.user import UserInDB
from app.notificaciones import routes as notification_routes


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

    def update_one(self, query: dict, update: dict):
        for doc in self.docs:
            if _matches(doc, query):
                doc.update(update.get("$set", {}))
                return


def _manager_user() -> UserInDB:
    return UserInDB(
        id=1,
        email="manager@example.com",
        first_name="Manager",
        last_name="NewsRadar",
        organization="NewsRadar",
        role_ids=[],
        role="manager",
    )


def test_update_alert_notification_settings_persists_channels(monkeypatch) -> None:
    alerts_col = FakeCollection(
        [
            {
                "id": 10,
                "user_id": 1,
                "name": "Energia",
                "descriptors": ["energia"],
                "categories": [],
                "cron_expression": "*/5 * * * *",
                "notification_channels": ["app", "email"],
                "enabled": True,
            }
        ]
    )
    monkeypatch.setattr(alert_routes, "alerts_col", alerts_col)

    result = alert_routes.update_alert_notification_settings(
        1,
        10,
        AlertNotificationSettingsUpdate(channels=["email"]),
        current_user=_manager_user(),
    )

    assert result.channels == ["email"]
    assert alerts_col.docs[0]["notification_channels"] == ["email"]


def test_list_user_notifications_only_returns_app_mailbox(monkeypatch) -> None:
    notifications_col = FakeCollection(
        [
            {
                "id": 1,
                "alert_id": 10,
                "user_id": 1,
                "timestamp": datetime(2026, 4, 26, 10, 0, tzinfo=timezone.utc),
                "subject": "Actualizacion 1",
                "metrics": [],
                "matches": [],
                "delivery_channels": ["app", "email"],
                "email_status": "sent",
                "email_sent_at": datetime(2026, 4, 26, 10, 0, tzinfo=timezone.utc),
                "email_error": None,
                "read_at": None,
            },
            {
                "id": 2,
                "alert_id": 11,
                "user_id": 1,
                "timestamp": datetime(2026, 4, 26, 9, 0, tzinfo=timezone.utc),
                "subject": "Actualizacion 2",
                "metrics": [],
                "matches": [],
                "delivery_channels": ["email"],
                "email_status": "sent",
                "email_sent_at": datetime(2026, 4, 26, 9, 0, tzinfo=timezone.utc),
                "email_error": None,
                "read_at": None,
            },
        ]
    )
    monkeypatch.setattr(notification_routes, "notifications_col", notifications_col)

    result = notification_routes.list_user_notifications(1, current_user=_manager_user())

    assert [item.id for item in result] == [1]


def test_mark_notification_read_updates_read_at(monkeypatch) -> None:
    notifications_col = FakeCollection(
        [
            {
                "id": 3,
                "alert_id": 12,
                "user_id": 1,
                "timestamp": datetime(2026, 4, 26, 8, 0, tzinfo=timezone.utc),
                "subject": "Actualizacion 3",
                "metrics": [],
                "matches": [],
                "delivery_channels": ["app"],
                "email_status": "skipped",
                "email_sent_at": None,
                "email_error": None,
                "read_at": None,
            }
        ]
    )
    monkeypatch.setattr(notification_routes, "notifications_col", notifications_col)

    result = notification_routes.mark_notification_read(
        1,
        3,
        current_user=_manager_user(),
    )

    assert result.id == 3
    assert notifications_col.docs[0]["read_at"] is not None


def _matches(doc: dict, query: dict) -> bool:
    for key, expected in query.items():
        actual = doc.get(key)
        if isinstance(actual, list) and not isinstance(expected, dict):
            if expected not in actual:
                return False
            continue
        if actual != expected:
            return False
    return True
