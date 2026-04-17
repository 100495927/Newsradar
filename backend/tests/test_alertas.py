import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

# Importamos tu app real desde app.py
from app.app import app

# Creamos el cliente de pruebas con tu aplicación
client = TestClient(app)

# --- TESTS DE INTEGRACIÓN (API REST) ---

def test_health_endpoint():
    """Prueba que el endpoint de health responde correctamente."""
    # Fíjate que usamos el prefijo /api/v1
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()

def test_crear_alerta_requiere_autenticacion():
    """Prueba que la creación de una alerta sin token de autenticación falla."""
    payload = {
        "name": "Alerta de prueba",
        "descriptors": ["tecnologia", "IA"],
        "cron_expression": "0 12 * * *"
    }
    
    # Intentamos hacer POST a una ruta protegida
    response = client.post("/api/v1/users/1/alerts", json=payload)
    
    # FastAPI/dependencies.py debe bloquearnos por no llevar un JWT válido
    assert response.status_code in [401, 403]

# --- TESTS UNITARIOS (Aislados) ---

def test_modelo_alerta_invalido():
    """Prueba que Pydantic rechaza alertas que no cumplen los requisitos."""
    from app.alertas.models import AlertCreate
    
    # El campo 'name' tiene min_length=1. Si pasamos vacío, debe lanzar error.
    with pytest.raises(ValidationError):
        AlertCreate(name="", cron_expression="0 12 * * *")