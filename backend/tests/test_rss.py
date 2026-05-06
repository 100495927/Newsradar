from __future__ import annotations

from uuid import uuid4

def test_rss_workflow(client, auth_headers):
    unique_suffix = uuid4().hex[:8]
    source_id = None
    channel_id = None

    try:
        categories_resp = client.get("/api/v1/categories", headers=auth_headers)
        assert categories_resp.status_code == 200
        category_id = categories_resp.json()[0]["id"]

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
        assert source_resp.json()["name"] == source_data["name"]
        assert source_resp.json()["url"] == source_data["url"]

        channel_data = {
            "url": f"https://www.elmundo.es/rss/portada.xml?testrun={unique_suffix}",
            "category_id": category_id,
        }
        rss_resp = client.post(
            f"/api/v1/information-sources/{source_id}/rss-channels",
            json=channel_data,
            headers=auth_headers,
        )
        assert rss_resp.status_code == 201
        channel_id = rss_resp.json()["id"]
        assert rss_resp.json()["category_id"] == category_id
        assert rss_resp.json()["information_source_id"] == source_id
        assert rss_resp.json()["url"] == channel_data["url"]

        list_resp = client.get(
            f"/api/v1/information-sources/{source_id}/rss-channels",
            headers=auth_headers,
        )
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1
        assert any(channel["id"] == channel_id for channel in list_resp.json())
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

def test_source_not_found(client, auth_headers):
    response = client.get("/api/v1/information-sources/9999", headers=auth_headers)
    assert response.status_code == 404
