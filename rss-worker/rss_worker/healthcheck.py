import sys
from shared.mongo import Database
import requests


def main() -> int:
    try:
        db = Database()
        cols_ext = set(db.db_app.list_collection_names())

        cols_req = [
            db.col_rss_entradas.NOMBRE_COLECCION,
            db.col_rss_fuentes.NOMBRE_COLECCION,
            db.col_rss_cat_iptc.NOMBRE_COLECCION,
            db.col_user_sesions.NOMBRE_COLECCION,
            db.col_users.NOMBRE_COLECCION,
            db.col_alertas.NOMBRE_COLECCION,
            db.col_notifications.NOMBRE_COLECCION,
            db.col_counters.NOMBRE_COLECCION,
        ]

        missing = [col for col in cols_req if col not in cols_ext]
        if missing:
            raise ValueError(f"Colecciones no encontradas: {', '.join(missing)}")
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
    from EntornoRSS import EntornoRSS

    entorno = EntornoRSS()
    url = f"http://localhost:{entorno.puerto_uvicorn}/openapi.json"

    response = requests.get(url, timeout=5)
    response.raise_for_status()
    print(f"Status Code: {response.status_code}")


if __name__ == "__main__":
    sys.exit(main())
