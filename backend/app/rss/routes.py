from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo.errors import DuplicateKeyError

from ..auth.user import UserInDB
from ..category.routes import ensure_category_exists
from ..dependencies import get_current_user
from ..store import information_sources_col, next_mongo_id, rss_channels_col, rss_fuentes_col
from .models import (
    InformationSource,
    InformationSourceCreate,
    InformationSourceUpdate,
    RSSChannel,
    RSSChannelCreate,
    RSSChannelUpdate,
)

router = APIRouter(tags=["information-sources", "rss-channels"])



def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_fuente(*parts: object) -> str:
    raw = "|".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _source_query(source_id: int) -> dict:
    return {
        "tipo": "source",
        "source_id": source_id,
        "deleted_at": {"$exists": False},
    }


def _channel_query(source_id: int, channel_id: int) -> dict:
    return {
        "tipo": "channel",
        "source_id": source_id,
        "channel_id": channel_id,
        "deleted_at": {"$exists": False},
    }


def _doc_to_source(doc: dict) -> InformationSource:
    return InformationSource(
        id=doc["id"],
        name=doc["name"],
        url=doc["url"],
    )


def _doc_to_channel(doc: dict) -> RSSChannel:
    return RSSChannel(
        id=doc["id"],
        information_source_id=doc["information_source_id"],
        url=doc["url"],
        category_id=doc["category_id"],
    )


def ensure_information_source_exists(source_id: int) -> dict:
    source = information_sources_col.find_one({"id": source_id}, {"_id": 0})
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    return source


def ensure_rss_for_source(source_id: int, channel_id: int) -> dict:
    channel = rss_channels_col.find_one(
        {"id": channel_id, "information_source_id": source_id}, {"_id": 0}
    )
    if not channel:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    return channel


@router.get("/information-sources", response_model=List[InformationSource])
def list_information_sources(_: UserInDB = Depends(get_current_user)) -> List[InformationSource]:
    cursor = information_sources_col.find({}, {"_id": 0}).sort("id", 1)
    return [_doc_to_source(doc) for doc in cursor]


@router.post("/information-sources", response_model=InformationSource, status_code=201)
def create_information_source(
    payload: InformationSourceCreate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    now = _utc_now()
    source_id = next_mongo_id("information_sources")
    source_url = str(payload.url)
    source_doc = {
        "hash_fuente": _hash_fuente("source", source_id, source_url),
        "medio": payload.name,
        "rss": None,
        "url": source_url,
        "tipo": "source",
        "source_id": source_id,
        "source_name": payload.name,
        "source_url": source_url,
        "channel_id": None,
        "category_id": None,
        "activo": False,
        "categoria_iptc": None,
        "creado": now,
        "actualizado": now,
    }

    try:
        rss_fuentes_col.insert_one(source_doc)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una fuente RSS registrada con esa URL",
        ) from exc

    return _doc_to_source(source_doc)


@router.get("/information-sources/{source_id}", response_model=InformationSource)
def get_information_source(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    return _doc_to_source(ensure_information_source_exists(source_id))


@router.put("/information-sources/{source_id}", response_model=InformationSource)
def update_information_source(
    source_id: int,
    payload: InformationSourceUpdate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    source = ensure_information_source_exists(source_id)
    update_data = payload.model_dump(exclude_unset=True)
    now = _utc_now()

    source_name = update_data.get("name", source["source_name"])
    source_url = str(update_data.get("url", source["source_url"]))
    set_fields = {
        "hash_fuente": _hash_fuente("source", source_id, source_url),
        "medio": source_name,
        "url": source_url,
        "source_name": source_name,
        "source_url": source_url,
        "actualizado": now,
    }

    try:
        rss_fuentes_col.update_one(_source_query(source_id), {"$set": set_fields})
        rss_fuentes_col.update_many(
            {
                "tipo": "channel",
                "source_id": source_id,
                "deleted_at": {"$exists": False},
            },
            {
                "$set": {
                    "source_name": source_name,
                    "source_url": source_url,
                    "medio": source_name,
                    "actualizado": now,
                }
            },
        )
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una fuente RSS registrada con esa URL",
        ) from exc

    updated_doc = rss_fuentes_col.find_one(_source_query(source_id), {"_id": 0})
    return _doc_to_source(updated_doc)


@router.delete("/information-sources/{source_id}", status_code=204)
def delete_information_source(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
) -> Response:
    ensure_information_source_exists(source_id)
    now = _utc_now()
    rss_fuentes_col.update_one(
        _source_query(source_id),
        {"$set": {"activo": False, "deleted_at": now, "actualizado": now}},
    )
    rss_fuentes_col.update_many(
        {
            "tipo": "channel",
            "source_id": source_id,
            "deleted_at": {"$exists": False},
        },
        {"$set": {"activo": False, "deleted_at": now, "actualizado": now}},
    )
    return Response(status_code=204)


@router.get("/information-sources/{source_id}/rss-channels", response_model=List[RSSChannel])
def list_source_channels(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
) -> List[RSSChannel]:
    ensure_information_source_exists(source_id)
    cursor = rss_channels_col.find(
        {"information_source_id": source_id}, {"_id": 0}
    ).sort("id", 1)
    return [_doc_to_channel(doc) for doc in cursor]


@router.post(
    "/information-sources/{source_id}/rss-channels",
    response_model=RSSChannel,
    status_code=201,
)
def create_source_channel(
    source_id: int,
    payload: RSSChannelCreate,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    source = ensure_information_source_exists(source_id)
    ensure_category_exists(payload.category_id)

    now = _utc_now()
    channel_id = next_mongo_id("rss_channels")
    channel_url = str(payload.url)
    channel_doc = {
        "hash_fuente": _hash_fuente("channel", source_id, channel_id, channel_url),
        "medio": source["source_name"],
        "rss": channel_url,
        "url": channel_url,
        "tipo": "channel",
        "source_id": source_id,
        "source_name": source["source_name"],
        "source_url": source["source_url"],
        "channel_id": channel_id,
        "category_id": payload.category_id,
        "activo": True,
        "categoria_iptc": None,
        "creado": now,
        "actualizado": now,
    }

    try:
        rss_fuentes_col.insert_one(channel_doc)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un canal RSS registrado con esa URL",
        ) from exc

    return _doc_to_channel(channel_doc)


@router.get(
    "/information-sources/{source_id}/rss-channels/{channel_id}",
    response_model=RSSChannel,
)
def get_source_channel(
    source_id: int,
    channel_id: int,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    ensure_information_source_exists(source_id)
    return _doc_to_channel(ensure_rss_for_source(source_id, channel_id))


@router.put(
    "/information-sources/{source_id}/rss-channels/{channel_id}",
    response_model=RSSChannel,
)
def update_source_channel(
    source_id: int,
    channel_id: int,
    payload: RSSChannelUpdate,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    ensure_information_source_exists(source_id)
    channel = ensure_rss_for_source(source_id, channel_id)
    update_data = payload.model_dump(exclude_unset=True)
    now = _utc_now()
    set_fields = {"actualizado": now}

    if "category_id" in update_data:
        ensure_category_exists(update_data["category_id"])
        set_fields["category_id"] = update_data["category_id"]

    if "url" in update_data:
        channel_url = str(update_data["url"])
        set_fields["url"] = channel_url
        set_fields["rss"] = channel_url
        set_fields["hash_fuente"] = _hash_fuente(
            "channel",
            source_id,
            channel_id,
            channel_url,
        )

    try:
        rss_fuentes_col.update_one(_channel_query(source_id, channel_id), {"$set": set_fields})
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un canal RSS registrado con esa URL",
        ) from exc

    updated_doc = rss_channels_col.find_one(
        {"id": channel_id, "information_source_id": source_id}, {"_id": 0}
    )
    return _doc_to_channel(updated_doc or channel)


@router.delete("/information-sources/{source_id}/rss-channels/{channel_id}", status_code=204)
def delete_source_channel(
    source_id: int,
    channel_id: int,
    _: UserInDB = Depends(get_current_user),
) -> Response:
    ensure_information_source_exists(source_id)
    ensure_rss_for_source(source_id, channel_id)
    now = _utc_now()
    rss_fuentes_col.update_one(
        _channel_query(source_id, channel_id),
        {"$set": {"activo": False, "deleted_at": now, "actualizado": now}},
    )
    return Response(status_code=204)
