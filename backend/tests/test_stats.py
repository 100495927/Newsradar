import pytest
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    login_data = {"email": "test_devops@newsradar.com", "password": "testpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_stats_lifecycle(auth_headers):
    # 1. Crear stats
    payload = {"metrics": [{"name": "cpu_usage", "value": 45.5}]}
    resp = client.post("/api/v1/stats", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    stats_id = resp.json()["id"]

    # 2. Obtener stats
    get_resp = client.get(f"/api/v1/stats/{stats_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["metrics"][0]["name"] == "cpu_usage"

    # 3. Eliminar
    del_resp = client.delete(f"/api/v1/stats/{stats_id}", headers=auth_headers)
    assert del_resp.status_code == 204