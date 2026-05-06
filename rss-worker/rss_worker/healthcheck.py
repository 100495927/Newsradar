import sys

from .runtime import RSS_WORKER_REQUIRED_COLLECTIONS, build_rss_worker_db


def main() -> int:
    try:
        db = build_rss_worker_db()
        db.ping()
        cols_ext = set(db.db_app.list_collection_names())
        missing = [
            col for col in RSS_WORKER_REQUIRED_COLLECTIONS if col not in cols_ext
        ]
        if missing:
            raise ValueError(f"Colecciones no encontradas: {', '.join(missing)}")
    except Exception as exc:
        print(f"Healthcheck Error: {exc}", file=sys.stderr)
        return 1
    print("Healthcheck Pass: worker RSS listo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
