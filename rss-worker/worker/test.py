import sys

from shared.mongo import Database


def main() -> int:
    try:
        db = Database()
        fuentes = db.col_rss_fuentes.lista_fuentes()
        if not fuentes:
            print("Healthcheck Fail: no hay fuentes RSS registradas.", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"Healthcheck Error: {exc}", file=sys.stderr)
        return 1

    print("Healthcheck Pass: worker con fuentes RSS registradas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
