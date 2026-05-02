from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote_plus, urlsplit

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
    sources = app_db["information_sources"]
    channels = app_db["rss_channels"]
    counters = app_db["counters"]
    now = datetime.now(timezone.utc)

    inserted = 0
    updated = 0
    source_ids_by_medium: dict[str, int] = {}

    for source in STANDARD_RSS_SOURCES:
        source_url = _source_url_from_feed_url(source.url)
        existing_source = sources.find_one(
            {
                "url": source_url,
                "deleted_at": {"$exists": False},
            },
            {"id": 1},
        )
        if existing_source is None:
            source_id = _next_counter(counters, "information_sources", now)
            sources.insert_one(
                {
                    "id": source_id,
                    "name": _source_name_from_medium(source.medio),
                    "url": source_url,
                    "active": True,
                    "created_at": now,
                    "updated_at": now,
                }
            )
        else:
            source_id = int(existing_source["id"])
            sources.update_one(
                {"id": source_id},
                {
                    "$set": {
                        "name": _source_name_from_medium(source.medio),
                        "active": True,
                        "updated_at": now,
                    }
                },
            )
        source_ids_by_medium[source.medio] = source_id

    for source in STANDARD_RSS_SOURCES:
        existing_channel = channels.find_one(
            {
                "url": source.url,
                "deleted_at": {"$exists": False},
            },
            {"id": 1},
        )
        channel_id = (
            int(existing_channel["id"])
            if existing_channel is not None
            else _next_counter(counters, "rss_channels", now)
        )
        result = channels.update_one(
            {"id": channel_id},
            {
                "$set": {
                    "id": channel_id,
                    "information_source_id": source_ids_by_medium[source.medio],
                    "url": source.url,
                    "active": source.activo,
                    "category_id": source.category_id,
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        if result.upserted_id is not None:
            inserted += 1
        elif result.modified_count > 0:
            updated += 1

    total = channels.count_documents(
        {
            "active": True,
            "deleted_at": {"$exists": False},
        }
    )
    print(
        "[rss-bootstrap] Canales RSS base reconciliados: "
        f"{len(STANDARD_RSS_SOURCES)} definidos, {inserted} insertados, {updated} actualizados, {total} activos"
    )
    return 0


def _next_counter(counters: pymongo.collection.Collection, name: str, now: datetime) -> int:
    result = counters.find_one_and_update(
        {"_id": name},
        {
            "$inc": {"seq": 1},
            "$set": {"updated_at": now},
        },
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER,
    )
    return int(result["seq"])


def _source_name_from_medium(medio: str) -> str:
    return " ".join(part.capitalize() for part in medio.split("_") if part)


def _source_url_from_feed_url(feed_url: str) -> str:
    parsed = urlsplit(feed_url)
    return f"{parsed.scheme}://{parsed.netloc}"


if __name__ == "__main__":
    raise SystemExit(main())
