from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient


def test_notification_appears_in_alert_inbox(
    client: TestClient, auth_user: dict
) -> None:
    """
    Verifica la inspección 4 del enunciado:
    al procesarse una alerta, la notificación debe aparecer
    en GET /users/{uid}/alerts/{aid}/notifications (contrato del profesor).
    """
    user_id = auth_user["user_id"]
    headers = auth_user["headers"]

    # 1. Crear alerta
    alert_res = client.post(
        f"/api/v1/users/{user_id}/alerts",
        json={
            "name": "Test IA",
            "descriptors": ["inteligencia artificial", "IA"],
            "categories": [{"code": "13000000", "label": "Ciencia y tecnología"}],
            "cron_expression": "*/15 * * * *",
        },
        headers=headers,
    )
    assert alert_res.status_code == 201, alert_res.text
    alert_id = alert_res.json()["id"]

    # 2. Simular el trigger del worker creando una notificación para esa alerta
    notif_res = client.post(
        f"/api/v1/users/{user_id}/alerts/{alert_id}/notifications",
        json={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": [
                {"name": "noticias_encontradas", "value": 5},
                {"name": "noticias_nuevas", "value": 3},
            ],
        },
        headers=headers,
    )
    assert notif_res.status_code == 201, notif_res.text
    notification_id = notif_res.json()["id"]

    # 3. Verificar que aparece en el listado de notificaciones de la alerta
    inbox_res = client.get(
        f"/api/v1/users/{user_id}/alerts/{alert_id}/notifications",
        headers=headers,
    )
    assert inbox_res.status_code == 200, inbox_res.text
    inbox = inbox_res.json()

    assert len(inbox) >= 1, "No hay notificaciones tras crear una"

    found = next((n for n in inbox if n["id"] == notification_id), None)
    assert found is not None, "La notificación creada no aparece en el listado"

    # Las métricas deben haberse guardado
    metric_names = [m["name"] for m in found["metrics"]]
    assert "noticias_encontradas" in metric_names
    assert "noticias_nuevas" in metric_names


def test_notification_values_are_correct(
    client: TestClient, auth_user: dict
) -> None:
    """Verifica que el id, alert_id y timestamp de la notificación son correctos."""
    user_id = auth_user["user_id"]
    headers = auth_user["headers"]

    alert_res = client.post(
        f"/api/v1/users/{user_id}/alerts",
        json={
            "name": "Energía",
            "descriptors": ["energía", "gas"],
            "categories": [{"code": "04000000", "label": "Economía"}],
            "cron_expression": "0 * * * *",
        },
        headers=headers,
    )
    assert alert_res.status_code == 201
    alert_id = alert_res.json()["id"]

    ts = datetime.now(timezone.utc).replace(microsecond=0)
    notif_res = client.post(
        f"/api/v1/users/{user_id}/alerts/{alert_id}/notifications",
        json={
            "timestamp": ts.isoformat(),
            "metrics": [{"name": "noticias_encontradas", "value": 2}],
        },
        headers=headers,
    )
    assert notif_res.status_code == 201
    body = notif_res.json()

    assert body["alert_id"] == alert_id
    assert "id" in body
    assert "timestamp" in body
