from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from backend.app.auth.user import UserInDB
from backend.app.category import routes as category_routes
from backend.app.category.models import Category
from backend.app.notificaciones import routes as notification_routes
from backend.app.notificaciones.models import NotificationCreate


class FakeChannelsCollection:
    def __init__(self, docs: list[dict] | None = None) -> None:
        self.docs = list(docs or [])

    def find_one(self, query: dict, *_args, **_kwargs):
        for doc in self.docs:
            if all(_matches_field(doc, key, value) for key, value in query.items()):
                return doc
        return None


class FakeCollection:
    def __init__(self, docs: list[dict] | None = None) -> None:
        self.docs = list(docs or [])

    def find_one(self, query: dict, *_args, **_kwargs):
        for doc in self.docs:
            if all(doc.get(key) == value for key, value in query.items()):
                return doc
        return None

    def insert_one(self, doc: dict) -> None:
        self.docs.append(dict(doc))


def _matches_field(doc: dict, key: str, value):
    if isinstance(value, dict) and "$exists" in value:
        return (key in doc) == bool(value["$exists"])
    return doc.get(key) == value


def _dummy_user() -> UserInDB:
    return UserInDB(
        id=7,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        organization="NewsRadar",
        role_ids=[1],
        password_hash="hashed",
        role="manager",
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        email_verified_at=datetime.now(timezone.utc),
        is_verified=True,
    )


def test_create_category_returns_iptc_category_without_mutating_store(monkeypatch) -> None:
    categories_store = {
        11000000: Category(id=11000000, name="Politica", source="IPTC"),
    }
    monkeypatch.setattr(category_routes, "categories_store", categories_store)

    before = dict(categories_store)
    response = category_routes.create_category(
        payload=category_routes.CategoryCreate(name="Ciencia y tecnología", source="IPTC"),
        _=_dummy_user(),
    )

    assert response.name == "Ciencia y tecnología"
    assert response.id == 13000000
    assert categories_store == before


def test_list_categories_returns_loaded_catalog(monkeypatch) -> None:
    monkeypatch.setattr(
        category_routes,
        "categories_store",
        {
            13000000: Category(id=13000000, name="Ciencia y tecnologia", source="IPTC"),
        },
    )

    response = category_routes.list_categories(_=_dummy_user())

    assert isinstance(response, list)
    assert any(item.id == 13000000 for item in response)


def test_delete_category_without_channels_is_noop(monkeypatch) -> None:
    monkeypatch.setattr(category_routes, "rss_channels_col", FakeChannelsCollection([]))

    response = category_routes.delete_category(category_id=9999, _=_dummy_user())

    assert response is None


def test_create_notification_uses_alert_delivery_channels(monkeypatch) -> None:
    alerts_col = FakeCollection(
        [
            {
                "id": 21,
                "user_id": 7,
                "notification_channels": ["app", "email"],
            }
        ]
    )
    notifications_col = FakeCollection([])

    monkeypatch.setattr(notification_routes, "alerts_col", alerts_col)
    monkeypatch.setattr(notification_routes, "notifications_col", notifications_col)
    monkeypatch.setattr(notification_routes, "next_mongo_id", lambda _key: 55)
    monkeypatch.setattr(notification_routes, "ensure_user_can_access", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        notification_routes,
        "ensure_alert_for_user",
        lambda user_id, alert_id: SimpleNamespace(id=alert_id, user_id=user_id, name="Alerta de prueba"),
    )

    payload = NotificationCreate(
        timestamp=datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc),
        metrics=[],
    )

    response = notification_routes.create_alert_notification(
        user_id=7,
        alert_id=21,
        payload=payload,
        current_user=_dummy_user(),
    )

    assert response.id == 55
    assert response.alert_id == 21
    assert notifications_col.docs[0]["delivery_channels"] == ["app", "email"]
    assert notifications_col.docs[0]["email_status"] == "pending"
