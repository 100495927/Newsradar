from __future__ import annotations

from uuid import uuid4

from backend.app.store import categories_store

def test_rss_workflow(client, auth_headers):
    unique_suffix = uuid4().hex[:8]
    category_id = None
    source_id = None
    channel_id = None

    try:
        # 1. Crear una categoría primero (necesaria para el canal RSS)
        cat_resp = client.post(
            "/api/v1/categories",
            json={"name": f"Tecnología {unique_suffix}", "source": "IPTC"},
            headers=auth_headers,
        )
        assert cat_resp.status_code == 201
        category_id = cat_resp.json()["id"]

        # 2. Crear una Fuente de Información
        source_data = {
            "name": f"El Mundo {unique_suffix}",
            "url": f"https://www.elmundo.es/?testrun={unique_suffix}",
        }
        source_resp = client.post(
            "/api/v1/information-sources",
            json=source_data,
            headers=auth_headers,
        )
        assert source_resp.status_code == 201
        source_id = source_resp.json()["id"]

        # 3. Crear un Canal RSS vinculado
        rss_data = {
            "url": f"https://www.elmundo.es/rss/portada.xml?testrun={unique_suffix}",
            "category_id": category_id,
        }
        rss_resp = client.post(
            f"/api/v1/information-sources/{source_id}/rss-channels",
            json=rss_data,
            headers=auth_headers,
        )
        assert rss_resp.status_code == 201
        channel_id = rss_resp.json()["id"]
        assert rss_resp.json()["category_id"] == category_id

        # 4. Listar canales de la fuente
        list_resp = client.get(
            f"/api/v1/information-sources/{source_id}/rss-channels",
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1
    finally:
        if source_id is not None and channel_id is not None:
            client.delete(
                f"/api/v1/information-sources/{source_id}/rss-channels/{channel_id}",
                headers=auth_headers,
            )
        if source_id is not None:
            client.delete(
                f"/api/v1/information-sources/{source_id}",
                headers=auth_headers,
            )
        if category_id is not None:
            categories_store.pop(category_id, None)

def test_source_not_found(client, auth_headers):
    response = client.get("/api/v1/information-sources/9999", headers=auth_headers)
    assert response.status_code == 404
