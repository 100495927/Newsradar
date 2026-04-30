def test_stats_lifecycle(client, auth_headers):
    # 1. Crear stats
    payload = {"metrics": [{"name": "cpu_usage", "value": 45.5}]}
    stats_id = None

    try:
        resp = client.post("/api/v1/stats", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        stats_id = resp.json()["id"]

        # 2. Obtener stats
        get_resp = client.get(f"/api/v1/stats/{stats_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["metrics"][0]["name"] == "cpu_usage"
    finally:
        if stats_id is not None:
            client.delete(f"/api/v1/stats/{stats_id}", headers=auth_headers)