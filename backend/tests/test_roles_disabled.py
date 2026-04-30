from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.auth import routes as auth_routes
from app.auth.user import Role, RoleCreate, RoleUpdate, UserCreate, UserInDB
from app.dependencies import ensure_user_can_access, user_has_manager_role


class FakeUsersCollection:
    def __init__(self, docs: list[dict] | None = None) -> None:
        self.docs = docs or []

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

    def update_one(self, query: dict, update: dict) -> SimpleNamespace:
        doc = self.find_one(query)
        if doc:
            doc.update(update.get("$set", {}))
            return SimpleNamespace(modified_count=1)
        return SimpleNamespace(modified_count=0)


def _user(user_id: int) -> UserInDB:
    return UserInDB(
        id=user_id,
        email=f"user{user_id}@example.com",
        first_name="User",
        last_name="Test",
        organization="NewsRadar",
        role_ids=[],
        role="reader",
    )


def test_register_ignores_payload_roles_and_persists_manager(monkeypatch) -> None:
    fake_users_col = FakeUsersCollection()
    monkeypatch.setattr(auth_routes, "users_col", fake_users_col)
    monkeypatch.setattr(auth_routes, "roles_store", {})

    payload = UserCreate(
        email="new.user@example.com",
        first_name="New",
        last_name="User",
        organization="NewsRadar",
        role_ids=[77, 88],
        password="secret123",
    )

    auth_routes.register(payload)

    assert len(fake_users_col.docs) == 1
    stored = fake_users_col.docs[0]
    assert stored["role"] == "manager"
    assert stored["role_ids"] == [1]
    assert "password_hash" in stored
    assert "password" not in stored


def test_create_user_ignores_payload_roles_and_persists_manager(monkeypatch) -> None:
    fake_users_col = FakeUsersCollection()
    monkeypatch.setattr(auth_routes, "users_col", fake_users_col)
    monkeypatch.setattr(auth_routes, "roles_store", {})

    payload = UserCreate(
        email="created.user@example.com",
        first_name="Created",
        last_name="User",
        organization="NewsRadar",
        role_ids=[99],
        password="secret123",
    )

    created = auth_routes.create_user(payload, _=_user(1))

    assert created.role_ids == [1]
    stored = fake_users_col.docs[0]
    assert stored["role"] == "manager"
    assert stored["role_ids"] == [1]


def test_role_routes_are_successful_noops(monkeypatch) -> None:
    monkeypatch.setattr(auth_routes, "roles_store", {1: Role(id=1, name="manager")})

    listed = auth_routes.list_roles(_=_user(1))
    created = auth_routes.create_role(RoleCreate(name="reader"), _=_user(1))
    fetched = auth_routes.get_role(42, _=_user(1))
    updated = auth_routes.update_role(77, RoleUpdate(name="admin"), _=_user(1))

    assert listed == [Role(id=1, name="manager")]
    assert created == Role(id=1, name="manager")
    assert fetched == Role(id=42, name="manager")
    assert updated == Role(id=77, name="manager")

    auth_routes.delete_role(99, _=_user(1))


def test_role_checks_are_disabled_but_user_scope_is_preserved() -> None:
    assert user_has_manager_role(_user(1)) is True
    ensure_user_can_access(1, _user(1))

    with pytest.raises(HTTPException) as excinfo:
        ensure_user_can_access(2, _user(1))

    assert excinfo.value.status_code == 403
