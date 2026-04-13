import sys

from shared.mongo import Database


def main() -> int:
    try:
        db_wrapper = Database()
        db_wrapper.db_admin.command("ping")

        colecciones_en_mongo = db_wrapper.db_app.list_collection_names()

        colecciones_esperadas = [
            db_wrapper.col_rss_entradas.NOMBRE_COLECCION,
            db_wrapper.col_rss_fuentes.NOMBRE_COLECCION,
            db_wrapper.col_user_sesions.NOMBRE_COLECCION,
            db_wrapper.col_users.NOMBRE_COLECCION,
        ]

        for col in colecciones_esperadas:
            if col not in colecciones_en_mongo:
                print(f"Healthcheck Fail: {col} no existe.", file=sys.stderr)
                return 1

        print("Healthcheck Pass: Verificado esquema y existencia de db.")
        return 0

    except Exception as e:
        print(f"Healthcheck Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
