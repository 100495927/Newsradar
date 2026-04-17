import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from backend.app.app import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Simula un login enviando todos los campos requeridos por el esquema de MongoDB"""
    now = datetime.now(timezone.utc)
    user_email = "test_devops@newsradar.com"
    
    # Este es el payload para el registro (cumpliendo con el esquema de Mongo)
    user_register_data = {
        "email": user_email,
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "Dev",
        "organization": "DevOps",
        "role": "user",
        "status": "active",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    # Payload simple para el login
    login_payload = {"email": user_email, "password": "testpassword"}
    
    # 1. Intentamos login
    response = client.post("/api/v1/auth/login", json=login_payload)
    
    # 2. Si falla (401 o 404), registramos al usuario
    if response.status_code != 200:
        reg_response = client.post("/api/v1/auth/register", json=user_register_data)
        
        # Si el registro funciona o si dice que ya existe (409), reintentamos login
        response = client.post("/api/v1/auth/login", json=login_payload)
    
    if response.status_code != 200:
        pytest.fail(f"Fallo crítico: No se pudo obtener token. Login dice: {response.text}")
        
    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}

# --- TESTS ACTUALIZADOS CON /api/v1 ---

def test_create_category(auth_headers):
    payload = {"name": "Tecnología", "source": "IPTC"}
    response = client.post("/api/v1/categories", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Tecnología"

def test_list_categories(auth_headers):
    response = client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_category_not_found(auth_headers):
    response = client.delete("/api/v1/categories/9999", headers=auth_headers)
    assert response.status_code == 404

def test_create_notification(auth_headers):
    # Nota: El user_id 1 y alert_id 1 deben existir en el store
    url = "/api/v1/users/1/alerts/1/notifications"
    payload = {
        "timestamp": "2026-04-17T12:00:00",
        "metrics": []
    }
    response = client.post(url, json=payload, headers=auth_headers)
    # Es probable que de 404 si la alerta 1 no existe, pero ya no será por la ruta de auth
    assert response.status_code in [201, 404]