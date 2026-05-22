from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from app.auth import routes as auth_routes
from app.auth.user import Role, UserCreate, UserInDB


class DuplicateOnInsertUsersCollection:
    def find_one(self, query: dict | None = None, sort: list[tuple[str, int]] | None = None):
        return None

    def insert_one(self, doc: dict) -> SimpleNamespace:
        raise DuplicateKeyError("duplicate key error")


def _user(user_id: int) -> UserInDB:
    return UserInDB(
        id=user_id,
        email=f"user{user_id}@example.com",
        first_name="User",
        last_name="Test",
        organization="NewsRadar",
        role_ids=[1],
        role="gestor",
    )


def test_create_user_maps_duplicate_key_race_to_conflict(monkeypatch) -> None:
    monkeypatch.setattr(auth_routes, "users_col", DuplicateOnInsertUsersCollection())
    monkeypatch.setattr(auth_routes, "roles_store", {1: Role(id=1, name="gestor")})
    monkeypatch.setattr(auth_routes, "next_mongo_id", lambda _key: 42)

    payload = UserCreate(
        email="race-user@example.com",
        first_name="Race",
        last_name="User",
        organization="NewsRadar",
        role_ids=[1],
        password="secret123",
    )

    with pytest.raises(HTTPException) as exc_info:
        auth_routes.create_user(payload, _=_user(1))

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "El email ya está registrado"
