from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import HTTPException

from backend.app.auth.user import UserInDB
from backend.app.category import routes as category_routes
from backend.app.category.models import Category
from backend.app.notificaciones import routes as notification_routes
from backend.app.notificaciones.models import NotificationCreate
from backend.app.rss import routes as rss_routes


class FakeChannelsCollection:
    def __init__(self, docs: list[dict] | None = None) -> None:
        self.docs = list(docs or [])

    def find_one(self, query: dict, *_args, **_kwargs):
        for doc in self.docs:
            if all(_matches_field(doc, key, value) for key, value in query.items()):
                return doc
        return None


class FakeCategoriesCollection:
    def __init__(self, docs: list[dict] | None = None) -> None:
        self.docs = list(docs or [])

    def insert_one(self, doc: dict) -> None:
        self.docs.append(dict(doc))

    def update_one(self, query: dict, update: dict, upsert: bool = False):
        for doc in self.docs:
            if all(doc.get(key) == value for key, value in query.items()):
                doc.update(update.get("$set", {}))
                return None

        if upsert:
            doc = dict(query)
            doc.update(update.get("$set", {}))
            self.docs.append(doc)
        return None

    def delete_one(self, query: dict):
        self.docs = [
            doc
            for doc in self.docs
            if not all(doc.get(key) == value for key, value in query.items())
        ]
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


def test_create_category_persists_new_category(monkeypatch) -> None:
    categories_store = {}
    categories_col = FakeCategoriesCollection()
    monkeypatch.setattr(category_routes, "categories_store", categories_store)
    monkeypatch.setattr(category_routes, "categories_col", categories_col)
    monkeypatch.setattr(category_routes, "next_mongo_id", lambda _key: 42)

    response = category_routes.create_category(
        payload=category_routes.CategoryCreate(name="Sociedad", source="IPTC"),
        _=_dummy_user(),
    )

    assert response.id == 14000000
    assert response.name == "Sociedad"
    assert categories_store[14000000] == response
    assert categories_col.docs[0]["_id"] == 14000000
    assert categories_col.docs[0]["descripciones"][0]["nombre"] == "Sociedad"


def test_create_category_rejects_non_catalog_name(monkeypatch) -> None:
    monkeypatch.setattr(category_routes, "categories_store", {})
    monkeypatch.setattr(category_routes, "categories_col", FakeCategoriesCollection())

    try:
        category_routes.create_category(
            payload=category_routes.CategoryCreate(name="Innovacion local", source="IPTC"),
            _=_dummy_user(),
        )
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("Expected non-catalog category error")


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


def test_update_category_persists_existing_category(monkeypatch) -> None:
    categories_store = {
        14000000: Category(id=14000000, name="Sociedad", source="IPTC"),
    }
    categories_col = FakeCategoriesCollection([{"_id": 14000000, "descripciones": []}])
    monkeypatch.setattr(category_routes, "categories_store", categories_store)
    monkeypatch.setattr(category_routes, "categories_col", categories_col)

    response = category_routes.update_category(
        category_id=14000000,
        payload=category_routes.CategoryUpdate(name="sociedad"),
        _=_dummy_user(),
    )

    assert response.id == 14000000
    assert response.name == "Sociedad"
    assert categories_store[14000000].name == "Sociedad"
    assert categories_col.docs[0]["descripciones"][0]["nombre"] == "Sociedad"


def test_update_category_missing_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(category_routes, "categories_store", {})

    try:
        category_routes.update_category(
            category_id=404,
            payload=category_routes.CategoryUpdate(name="No existe"),
            _=_dummy_user(),
        )
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected missing category error")


def test_update_category_rejects_name_for_other_catalog_id(monkeypatch) -> None:
    monkeypatch.setattr(
        category_routes,
        "categories_store",
        {
            11000000: Category(id=11000000, name="Política", source="IPTC"),
            14000000: Category(id=14000000, name="Sociedad", source="IPTC"),
        },
    )
    monkeypatch.setattr(category_routes, "categories_col", FakeCategoriesCollection())

    try:
        category_routes.update_category(
            category_id=14000000,
            payload=category_routes.CategoryUpdate(name="Política"),
            _=_dummy_user(),
        )
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("Expected catalog ID/name mismatch")


def test_delete_category_with_active_rss_channel_keeps_channel(monkeypatch) -> None:
    categories_store = {
        14000000: Category(id=14000000, name="Sociedad", source="IPTC"),
    }
    categories_col = FakeCategoriesCollection([{"_id": 14000000, "descripciones": []}])
    channels_col = FakeChannelsCollection([{"category_id": 14000000}])
    monkeypatch.setattr(category_routes, "categories_store", categories_store)
    monkeypatch.setattr(category_routes, "categories_col", categories_col)

    response = category_routes.delete_category(category_id=14000000, _=_dummy_user())

    assert response is None
    assert 14000000 not in categories_store
    assert channels_col.docs == [{"category_id": 14000000}]


def test_delete_category_missing_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(category_routes, "categories_store", {})

    try:
        category_routes.delete_category(category_id=404, _=_dummy_user())
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected missing category error")


def test_delete_category_without_channels_removes_category(monkeypatch) -> None:
    categories_store = {
        7000000: Category(id=7000000, name="Salud", source="IPTC"),
    }
    categories_col = FakeCategoriesCollection([{"_id": 7000000, "descripciones": []}])
    monkeypatch.setattr(category_routes, "categories_store", categories_store)
    monkeypatch.setattr(category_routes, "categories_col", categories_col)

    response = category_routes.delete_category(category_id=7000000, _=_dummy_user())

    assert response is None
    assert 7000000 not in categories_store
    assert categories_col.docs == []


def test_create_rss_channel_rejects_missing_category(monkeypatch) -> None:
    monkeypatch.setattr(category_routes, "categories_store", {})
    monkeypatch.setattr(rss_routes, "ensure_information_source_exists", lambda _source_id: {"id": 1})

    try:
        rss_routes.create_source_channel(
            source_id=1,
            payload=rss_routes.RSSChannelCreate(url="https://example.com/rss.xml", category_id=999),
            _=_dummy_user(),
        )
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected missing category error")


def test_update_rss_channel_rejects_missing_category(monkeypatch) -> None:
    monkeypatch.setattr(category_routes, "categories_store", {})
    monkeypatch.setattr(rss_routes, "ensure_information_source_exists", lambda _source_id: {"id": 1})
    monkeypatch.setattr(
        rss_routes,
        "ensure_rss_for_source",
        lambda _source_id, _channel_id: {
            "id": 7,
            "information_source_id": 1,
            "url": "https://example.com/rss.xml",
            "category_id": 42,
        },
    )

    try:
        rss_routes.update_source_channel(
            source_id=1,
            channel_id=7,
            payload=rss_routes.RSSChannelUpdate(category_id=999),
            _=_dummy_user(),
        )
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("Expected missing category error")


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
