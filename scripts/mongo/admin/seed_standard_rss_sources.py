from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote_plus

import pymongo

from shared.mongo.EntornoDB import EntornoDB
from shared.rss_seed_sources import STANDARD_RSS_SOURCES


def build_app_uri(entorno: EntornoDB) -> str:
    app_user = quote_plus(entorno.app_usuario)
    app_password = quote_plus(entorno.app_contraseña)
    return (
        f"mongodb://{app_user}:{app_password}"
        f"@{entorno.host}:{entorno.puerto}/{entorno.app_db_name}"
        f"?authSource={entorno.app_db_name}"
    )


def main() -> int:
    entorno = EntornoDB()
    client = pymongo.MongoClient(build_app_uri(entorno))
    app_db = client[entorno.app_db_name]
    collection = app_db["rss_fuentes"]
    now = datetime.now(timezone.utc)

    inserted = 0
    updated = 0

    for source in STANDARD_RSS_SOURCES:
        doc = source.to_mongo(now=now)
        result = collection.update_one(
            {"hash_fuente": doc["hash_fuente"]},
            {
                "$set": {
                    "medio": doc["medio"],
                    "rss": doc["rss"],
                    "url": doc["url"],
                    "tipo": doc["tipo"],
                    "activo": doc["activo"],
                    "category_id": doc["category_id"],
                    "actualizado": now,
                },
                "$setOnInsert": {"creado": now},
            },
            upsert=True,
        )
        if result.upserted_id is not None:
            inserted += 1
        elif result.modified_count > 0:
            updated += 1

    total = collection.count_documents(
        {
            "activo": True,
            "$or": [{"tipo": "channel"}, {"tipo": {"$exists": False}}],
            "deleted_at": {"$exists": False},
        }
    )
    print(
        "[rss-bootstrap] Fuentes RSS base reconciliadas: "
        f"{len(STANDARD_RSS_SOURCES)} definidas, {inserted} insertadas, {updated} actualizadas, {total} activas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
