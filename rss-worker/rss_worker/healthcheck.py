import sys

from rss_worker.settings import RssWorkerSettings
from shared.mongo import Database


def main() -> int:
    try:
        db = Database()
        cols_ext = db.db_admin.list_collection_names()

        cols_req = [
            db.col_rss_entradas.NOMBRE_COLECCION,
            db.col_rss_fuentes.NOMBRE_COLECCION,
            db.col_user_sesions.NOMBRE_COLECCION,
            db.col_users.NOMBRE_COLECCION,
        ]

        for col in cols_req:
            if col not in cols_ext:
                raise ValueError(f"Colecion {col} no encontradas")
    except Exception as exc:
        print(f"Healthcheck Error: {exc}", file=sys.stderr)
        return 1

    try:
        test_uvicorn()
    except Exception as exc:
        print(f"Healthcheck Error: {exc}", file=sys.stderr)
        return 1
    print("Healthcheck Pass: worker con fuentes RSS registradas.")
    return 0


def test_uvicorn():
    import requests

    settings = RssWorkerSettings.from_env()
    url = f"http://localhost:{settings.puerto_uvicorn}/fuentes"
    data = {
        "medio": "Test Media",
        "rss": "https://example.com/rss",
        "url": "https://example.com",
        "activo": False,
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
    except Exception as e:
        print(f"Uvicorn is not responding: {e}")


if __name__ == "__main__":
    sys.exit(main())
