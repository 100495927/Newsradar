from __future__ import annotations

from types import SimpleNamespace

from app import app as app_module


class FakeUsersCollection:
    def __init__(self) -> None:
        self.docs: list[dict] = []

    def find_one(self, query: dict | None = None, sort: list[tuple[str, int]] | None = None):
        if sort:
            if not self.docs:
                return None
            field_name, direction = sort[0]
            if direction < 0:
                return max(self.docs, key=lambda doc: doc.get(field_name, 0))
            return min(self.docs, key=lambda doc: doc.get(field_name, 0))

        query = query or {}
        for doc in self.docs:
            if all(doc.get(key) == value for key, value in query.items()):
                return doc
        return None

    def insert_one(self, doc: dict) -> SimpleNamespace:
        self.docs.append(doc)
        return SimpleNamespace(inserted_id=doc.get("id"))


def test_create_seed_data_creates_default_users_once(monkeypatch):
    fake_users_col = FakeUsersCollection()
    monkeypatch.setattr(app_module, "users_col", fake_users_col)
    monkeypatch.setattr(app_module, "roles_store", {})
    monkeypatch.setattr(
        app_module,
        "counters",
        {
            "roles": 1,
            "users": 1,
            "alerts": 1,
            "categories": 1,
            "notifications": 1,
            "information_sources": 1,
            "rss_channels": 1,
            "stats": 1,
        },
    )

    app_module.create_seed_data()
    app_module.create_seed_data()

    assert {role.name for role in app_module.roles_store.values()} == {
        "admin",
        "manager",
        "reader",
    }
    assert {doc["email"] for doc in fake_users_col.docs} == {
        "AdminDefault@newsradar.local",
        "GestorDefault@newsradar.local",
        "LectorDefault@newsradar.local",
    }
    assert len(fake_users_col.docs) == 3
    assert all(doc["password_hash"] for doc in fake_users_col.docs)
    assert all(doc["status"] == "active" for doc in fake_users_col.docs)
    assert all(doc["is_verified"] is True for doc in fake_users_col.docs)
