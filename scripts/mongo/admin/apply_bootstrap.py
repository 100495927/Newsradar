from __future__ import annotations

from urllib.parse import quote_plus

import pymongo

from shared.mongo.EntornoDB import EntornoDB
from shared.mongo.bootstrap_spec import COLLECTION_SPECS


def build_root_uri(entorno: EntornoDB) -> str:
    root_user = quote_plus(entorno.root_usuario)
    root_password = quote_plus(entorno.root_contraseña)
    return (
        f"mongodb://{root_user}:{root_password}"
        f"@{entorno.host}:{entorno.puerto}/{entorno.root_db_name}"
        f"?authSource={entorno.root_db_name}"
    )


def ensure_app_user(admin_db: pymongo.database.Database, entorno: EntornoDB) -> None:
    user_info = admin_db.command("usersInfo", entorno.app_usuario)
    if user_info.get("users"):
        admin_db.command(
            "updateUser",
            entorno.app_usuario,
            pwd=entorno.app_contraseña,
            roles=[{"role": "readWrite", "db": entorno.app_db_name}],
        )
        print(f"[mongo-admin] Usuario de aplicacion actualizado: {entorno.app_usuario}")
        return

    admin_db.command(
        "createUser",
        entorno.app_usuario,
        pwd=entorno.app_contraseña,
        roles=[{"role": "readWrite", "db": entorno.app_db_name}],
    )
    print(f"[mongo-admin] Usuario de aplicacion creado: {entorno.app_usuario}")


def ensure_collection(
    app_db: pymongo.database.Database, name: str, validator: dict
) -> None:
    collection_names = app_db.list_collection_names()
    if name in collection_names:
        app_db.command("collMod", name, validator=validator, validationLevel="moderate")
        print(f"[mongo-admin] Validador actualizado: {name}")
        return

    app_db.create_collection(name, validator=validator, validationLevel="moderate")
    print(f"[mongo-admin] Coleccion creada: {name}")


def ensure_indexes(app_db: pymongo.database.Database, name: str, indexes: list[dict]) -> None:
    collection = app_db[name]
    for index in indexes:
        collection.create_index(index["keys"], **index["kwargs"])
        print(f"[mongo-admin] Indice asegurado: {name}.{index['kwargs']['name']}")


def main() -> int:
    entorno = EntornoDB(require_root=True)
    client = pymongo.MongoClient(build_root_uri(entorno))
    admin_db = client[entorno.app_db_name]

    print("[mongo-admin] Aplicando bootstrap de MongoDB")
    admin_db.command("ping")
    ensure_app_user(admin_db, entorno)

    for spec in COLLECTION_SPECS:
        ensure_collection(admin_db, spec["name"], spec["validator"])
        ensure_indexes(admin_db, spec["name"], spec["indexes"])

    print("[mongo-admin] Bootstrap aplicado correctamente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
