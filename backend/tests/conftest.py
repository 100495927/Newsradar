from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.app.app import app
from backend.app.store import users_col


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_user(client: TestClient) -> dict[str, object]:
    email = f"test_devops_{uuid4().hex[:8]}@newsradar.com"
    password = "testpassword"
    register_payload = {
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "Dev",
        "organization": "DevOps",
        "role_ids": [1],
    }

    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    user_doc = users_col.find_one({"email": email}, {"_id": 0})
    assert user_doc is not None

    context = {
        "email": email,
        "user_id": user_doc["id"],
        "headers": {"Authorization": f"Bearer {login_response.json()['access_token']}"},
    }

    yield context

    client.delete(f"/api/v1/users/{context['user_id']}", headers=context["headers"])


@pytest.fixture
def auth_headers(auth_user: dict[str, object]) -> dict[str, str]:
    return auth_user["headers"]