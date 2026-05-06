from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..auth.user import UserInDB
from ..category.routes import ensure_category_exists
from ..dependencies import get_current_user
from ..store import information_sources_col, next_mongo_id, rss_channels_col
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


def _doc_to_source(doc: dict) -> InformationSource:
    return InformationSource(id=doc["id"], name=doc["name"], url=doc["url"])


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


# ---------------------------------------------------------------------------
# Information Sources
# ---------------------------------------------------------------------------

@router.get("/information-sources", response_model=List[InformationSource])
def list_information_sources(_: UserInDB = Depends(get_current_user)) -> List[InformationSource]:
    cursor = information_sources_col.find({}, {"_id": 0}).sort("id", 1)
    return [_doc_to_source(doc) for doc in cursor]


@router.post("/information-sources", response_model=InformationSource, status_code=201)
def create_information_source(
    payload: InformationSourceCreate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    if information_sources_col.find_one({"url": str(payload.url)}):
        raise HTTPException(status_code=409, detail="Ya existe una fuente con esa URL")
    now = _utc_now()
    source_id = next_mongo_id("information_sources")
    doc = {
        "id": source_id,
        "name": payload.name,
        "url": str(payload.url),
        "active": True,
        "created_at": now,
        "updated_at": now,
    }
    information_sources_col.insert_one(doc)
    return _doc_to_source(doc)


@router.get("/information-sources/{source_id}", response_model=InformationSource)
def get_information_source(
    source_id: int, _: UserInDB = Depends(get_current_user)
) -> InformationSource:
    return _doc_to_source(ensure_information_source_exists(source_id))


@router.put("/information-sources/{source_id}", response_model=InformationSource)
def update_information_source(
    source_id: int,
    payload: InformationSourceUpdate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    ensure_information_source_exists(source_id)
    data = payload.model_dump(exclude_unset=True)
    if "url" in data:
        data["url"] = str(data["url"])
    data["updated_at"] = _utc_now()
    information_sources_col.update_one({"id": source_id}, {"$set": data})
    return _doc_to_source(information_sources_col.find_one({"id": source_id}, {"_id": 0}))


@router.delete("/information-sources/{source_id}", status_code=204)
def delete_information_source(
    source_id: int, _: UserInDB = Depends(get_current_user)
) -> Response:
    ensure_information_source_exists(source_id)
    information_sources_col.delete_one({"id": source_id})
    rss_channels_col.delete_many({"information_source_id": source_id})
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# RSS Channels
# ---------------------------------------------------------------------------

@router.get(
    "/information-sources/{source_id}/rss-channels", response_model=List[RSSChannel]
)
def list_source_channels(
    source_id: int, _: UserInDB = Depends(get_current_user)
) -> List[RSSChannel]:
    ensure_information_source_exists(source_id)
    cursor = rss_channels_col.find({"information_source_id": source_id}, {"_id": 0}).sort("id", 1)
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
    ensure_information_source_exists(source_id)
    ensure_category_exists(payload.category_id)
    if rss_channels_col.find_one({"information_source_id": source_id, "url": str(payload.url)}):
        raise HTTPException(status_code=409, detail="Ya existe un canal con esa URL para esta fuente")
    now = _utc_now()
    channel_id = next_mongo_id("rss_channels")
    doc = {
        "id": channel_id,
        "information_source_id": source_id,
        "url": str(payload.url),
        "category_id": payload.category_id,
        "active": True,
        "created_at": now,
        "updated_at": now,
    }
    rss_channels_col.insert_one(doc)
    return _doc_to_channel(doc)


@router.get(
    "/information-sources/{source_id}/rss-channels/{channel_id}",
    response_model=RSSChannel,
)
def get_source_channel(
    source_id: int, channel_id: int, _: UserInDB = Depends(get_current_user)
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
    ensure_rss_for_source(source_id, channel_id)
    data = payload.model_dump(exclude_unset=True)
    if "url" in data:
        data["url"] = str(data["url"])
    if "category_id" in data:
        ensure_category_exists(data["category_id"])
    data["updated_at"] = _utc_now()
    rss_channels_col.update_one(
        {"id": channel_id, "information_source_id": source_id}, {"$set": data}
    )
    return _doc_to_channel(
        rss_channels_col.find_one({"id": channel_id, "information_source_id": source_id}, {"_id": 0})
    )


@router.delete("/information-sources/{source_id}/rss-channels/{channel_id}", status_code=204)
def delete_source_channel(
    source_id: int, channel_id: int, _: UserInDB = Depends(get_current_user)
) -> Response:
    ensure_information_source_exists(source_id)
    ensure_rss_for_source(source_id, channel_id)
    rss_channels_col.delete_one({"id": channel_id, "information_source_id": source_id})
    return Response(status_code=204)
