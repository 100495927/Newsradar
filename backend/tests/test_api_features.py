from __future__ import annotations

from uuid import uuid4

def test_create_category(client, auth_headers):
    before = client.get("/api/v1/categories", headers=auth_headers)
    payload = {"name": "Ciencia y tecnología", "source": "IPTC"}
    response = client.post("/api/v1/categories", json=payload, headers=auth_headers)
    after = client.get("/api/v1/categories", headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["name"] == "Ciencia y tecnología"
    assert response.json()["id"] == 13000000
    assert before.json() == after.json()

def test_list_categories(client, auth_headers):
    response = client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(item["id"] == 13000000 for item in response.json())

def test_delete_category_not_found(client, auth_headers):
    before = client.get("/api/v1/categories", headers=auth_headers)
    response = client.delete("/api/v1/categories/9999", headers=auth_headers)
    after = client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 204
    assert before.json() == after.json()

def test_create_notification(client, auth_user):
    alert_payload = {
        "name": f"Alerta de prueba {uuid4().hex[:8]}",
        "descriptors": ["tecnologia", "IA"],
        "categories": [{"code": "13000000", "label": "Ciencia y tecnología"}],
        "rss_channels_ids": [],
        "information_sources_ids": [],
        "cron_expression": "0 12 * * *",
    }

    alert_response = client.post(
        f"/api/v1/users/{auth_user['user_id']}/alerts",
        json=alert_payload,
        headers=auth_user["headers"],
    )
    assert alert_response.status_code == 201
    alert_id = alert_response.json()["id"]

    notification_payload = {
        "timestamp": "2026-04-17T12:00:00Z",
        "metrics": [],
    }
    notification_response = client.post(
        f"/api/v1/users/{auth_user['user_id']}/alerts/{alert_id}/notifications",
        json=notification_payload,
        headers=auth_user["headers"],
    )
    assert notification_response.status_code == 201
    assert notification_response.json()["alert_id"] == alert_id

    delete_response = client.delete(
        f"/api/v1/users/{auth_user['user_id']}/alerts/{alert_id}",
        headers=auth_user["headers"],
    )
    assert delete_response.status_code == 204
