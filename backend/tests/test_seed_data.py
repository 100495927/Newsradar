from __future__ import annotations

from app import app as app_module
from shared.iptc_catalog import IPTC_TOP_LEVEL_CATEGORIES


class FakeCursor:
    def __init__(self, docs: list[dict]) -> None:
        self.docs = list(docs)

    def sort(self, field_name: str, direction: int):
        reverse = direction < 0
        return sorted(self.docs, key=lambda doc: doc.get(field_name, 0), reverse=reverse)


class FakeUsersCollection:
    def __init__(self, docs: list[dict] | None = None) -> None:
        self.docs = list(docs or [])

    def find_one(self, query: dict | None = None, sort: list[tuple[str, int]] | None = None):
        if sort:
            if not self.docs:
                return None
            field_name, direction = sort[0]
            reverse = direction < 0
            return sorted(self.docs, key=lambda doc: doc.get(field_name, 0), reverse=reverse)[0]

        query = query or {}
        for doc in self.docs:
            if all(doc.get(key) == value for key, value in query.items()):
                return doc
        return None


class FakeCategoriesCollection:
    def __init__(self, docs: list[dict] | None = None) -> None:
        self.docs = list(docs or [])

    def find(self, *_args, **_kwargs):
        return FakeCursor(self.docs)


def test_create_seed_data_loads_categories_from_mongo_and_syncs_user_counter(monkeypatch):
    fake_users_col = FakeUsersCollection(docs=[{"id": 7}])
    fake_categories_col = FakeCategoriesCollection(
        docs=[
            {
                "_id": 11000000,
                "descripciones": [{"idioma": "es", "nombre": "Política"}],
            },
            {
                "_id": 15000000,
                "descripciones": [{"idioma": "es", "nombre": "Deporte"}],
            },
        ]
    )
    monkeypatch.setattr(app_module, "users_col", fake_users_col)
    monkeypatch.setattr(app_module, "categories_col", fake_categories_col)
    monkeypatch.setattr(app_module, "roles_store", {})
    monkeypatch.setattr(app_module, "categories_store", {})
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

    assert app_module.counters["users"] == 8
    assert {role.name for role in app_module.roles_store.values()} == {"manager"}
    assert app_module.categories_store[11000000].name == "Política"
    assert app_module.categories_store[15000000].name == "Deporte"


def test_create_seed_data_falls_back_to_static_catalog_when_collection_is_empty(monkeypatch):
    fake_users_col = FakeUsersCollection()
    fake_categories_col = FakeCategoriesCollection()
    monkeypatch.setattr(app_module, "users_col", fake_users_col)
    monkeypatch.setattr(app_module, "categories_col", fake_categories_col)
    monkeypatch.setattr(app_module, "roles_store", {})
    monkeypatch.setattr(app_module, "categories_store", {})
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

    assert len(app_module.categories_store) == len(IPTC_TOP_LEVEL_CATEGORIES)
    assert app_module.categories_store[11000000].name == "Política"
