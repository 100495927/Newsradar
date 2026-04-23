import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Obtiene token de admin/reader para las pruebas."""
    login_data = {"email": "test_devops@newsradar.com", "password": "testpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_rss_workflow(auth_headers):
    unique_suffix = uuid4().hex[:8]

    # 1. Crear una categoría primero (necesaria para el canal RSS)
    cat_resp = client.post("/api/v1/categories", 
                          json={"name": "Tecnología", "description": "Tech news"}, 
                          headers=auth_headers)
    assert cat_resp.status_code == 201
    cat_id = cat_resp.json()["id"]

    # 2. Crear una Fuente de Información
    source_data = {
        "name": f"El Mundo {unique_suffix}",
        "url": f"https://www.elmundo.es/?testrun={unique_suffix}",
    }
    source_resp = client.post("/api/v1/information-sources", json=source_data, headers=auth_headers)
    assert source_resp.status_code == 201
    source_id = source_resp.json()["id"]

    # 3. Crear un Canal RSS vinculado
    rss_data = {
        "url": f"https://www.elmundo.es/rss/portada.xml?testrun={unique_suffix}",
        "category_id": cat_id,
    }
    rss_resp = client.post(f"/api/v1/information-sources/{source_id}/rss-channels", 
                           json=rss_data, headers=auth_headers)
    assert rss_resp.status_code == 201
    assert rss_resp.json()["category_id"] == cat_id

    # 4. Listar canales de la fuente
    list_resp = client.get(f"/api/v1/information-sources/{source_id}/rss-channels", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

def test_source_not_found(auth_headers):
    response = client.get("/api/v1/information-sources/9999", headers=auth_headers)
    assert response.status_code == 404
