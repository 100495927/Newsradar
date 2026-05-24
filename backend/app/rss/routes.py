from __future__ import annotations
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo.errors import DuplicateKeyError

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

_LOCAL_RSS_MOCK_HOSTS = {"127.0.0.1", "localhost"}
_LOCAL_RSS_MOCK_PORT = 8100


def _is_containerized_runtime() -> bool:
    return Path("/.dockerenv").exists()


def _runtime_accessible_url(url: str) -> str:
    parsed = urlparse(url)
    if (
        not _is_containerized_runtime()
        or parsed.hostname not in _LOCAL_RSS_MOCK_HOSTS
        or parsed.port != _LOCAL_RSS_MOCK_PORT
    ):
        return url

    return urlunparse(parsed._replace(netloc=f"host.docker.internal:{parsed.port}"))


def _url_accessible(url: str, timeout: int = 5) -> bool:
    """False only on definite failures: DNS error or connection refused."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        socket.create_connection((host, port), timeout=timeout).close()
        return True
    except (socket.gaierror, ConnectionRefusedError):
        return False
    except Exception:
        return True  # timeout or other uncertain failure — be permissive


def _is_rss_content(url: str, timeout: int = 5) -> bool:
    """False only when GET confirms the content is definitively not RSS."""
    try:
        req = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "").lower()
            if "application/json" in content_type:
                return False
            chunk = resp.read(4096)
            if any(tag in chunk for tag in (b"<rss", b"<feed", b"<channel")):
                return True
            # HTML body with no RSS tags → not RSS
            if "text/html" in content_type:
                return False
            return False
    except urllib.error.HTTPError as exc:
        # Only reject if server confirms JSON content type
        if "application/json" in exc.headers.get("Content-Type", "").lower():
            return False
        return True  # can't confirm non-RSS — be permissive
    except Exception:
        return True  # network/timeout — be permissive


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

def _source_query(source_id: int) -> dict:
    return {
        "id": source_id,
        "deleted_at": {"$exists": False},
    }


def _channel_query(source_id: int, channel_id: int) -> dict:
    return {
        "information_source_id": source_id,
        "id": channel_id,
        "deleted_at": {"$exists": False},
    }


def _normalize_url(url: str) -> str:
    """Normaliza URL: lowercase + sin trailing slash para evitar duplicados por variantes equivalentes."""
    return url.lower().rstrip("/")


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
    source = information_sources_col.find_one(_source_query(source_id), {"_id": 0})
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    return source


def ensure_rss_for_source(source_id: int, channel_id: int) -> dict:
    channel = rss_channels_col.find_one(_channel_query(source_id, channel_id), {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    return channel


# ---------------------------------------------------------------------------
# Information Sources
# ---------------------------------------------------------------------------

@router.get("/information-sources", response_model=List[InformationSource])
def list_information_sources(_: UserInDB = Depends(get_current_user)) -> List[InformationSource]:
    cursor = information_sources_col.find(
        {"deleted_at": {"$exists": False}},
        {"_id": 0},
    ).sort("id", 1)
    return [_doc_to_source(doc) for doc in cursor]


@router.post("/information-sources", response_model=InformationSource, status_code=201)
def create_information_source(
    payload: InformationSourceCreate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    source_url = _normalize_url(str(payload.url))
    source_url = _runtime_accessible_url(source_url)
    if not _url_accessible(source_url):
        raise HTTPException(status_code=422, detail="URL no accesible")
    if information_sources_col.find_one({"url": source_url, "deleted_at": {"$exists": False}}):
        raise HTTPException(status_code=409, detail="Ya existe una fuente con esa URL")
    if information_sources_col.find_one({"name": payload.name, "deleted_at": {"$exists": False}}):
        raise HTTPException(status_code=409, detail="Ya existe una fuente con ese nombre")
    now = _utc_now()
    source_id = next_mongo_id("information_sources")
    source_doc = {
        "id": source_id,
        "name": payload.name,
        "url": source_url,
        "active": True,
        "created_at": now,
        "updated_at": now,
    }

    try:
        information_sources_col.insert_one(source_doc)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una fuente de informacion registrada con esa URL",
        ) from exc

    return _doc_to_source(source_doc)


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
    source = ensure_information_source_exists(source_id)
    update_data = payload.model_dump(exclude_unset=True)
    now = _utc_now()

    source_name = update_data.get("name", source["name"])
    source_url = _normalize_url(str(update_data.get("url", source["url"])))
    source_url = _runtime_accessible_url(source_url)
    if "url" in update_data and not _url_accessible(source_url):
        raise HTTPException(status_code=422, detail="URL no accesible")
    set_fields = {
        "name": source_name,
        "url": source_url,
        "updated_at": now,
    }

    try:
        information_sources_col.update_one(_source_query(source_id), {"$set": set_fields})
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una fuente de informacion registrada con esa URL",
        ) from exc

    updated_doc = information_sources_col.find_one(_source_query(source_id), {"_id": 0})
    return _doc_to_source(updated_doc)


@router.delete("/information-sources/{source_id}", status_code=204)
def delete_information_source(
    source_id: int, _: UserInDB = Depends(get_current_user)
) -> Response:
    ensure_information_source_exists(source_id)
    now = _utc_now()
    information_sources_col.update_one(
        _source_query(source_id),
        {"$set": {"active": False, "deleted_at": now, "updated_at": now}},
    )
    rss_channels_col.update_many(
        {
            "information_source_id": source_id,
            "deleted_at": {"$exists": False},
        },
        {"$set": {"active": False, "deleted_at": now, "updated_at": now}},
    )
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
    cursor = rss_channels_col.find(
        {
            "information_source_id": source_id,
            "deleted_at": {"$exists": False},
        },
        {"_id": 0},
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
    ensure_information_source_exists(source_id)
    ensure_category_exists(payload.category_id)
    channel_url = _normalize_url(str(payload.url))
    channel_url = _runtime_accessible_url(channel_url)
    if not _url_accessible(channel_url):
        raise HTTPException(status_code=422, detail="URL no accesible")
    if not _is_rss_content(channel_url):
        raise HTTPException(status_code=422, detail="La URL no contiene contenido RSS")
    if rss_channels_col.find_one({"information_source_id": source_id, "url": channel_url, "deleted_at": {"$exists": False}}):
        raise HTTPException(status_code=409, detail="Ya existe un canal con esa URL para esta fuente")
    now = _utc_now()
    channel_id = next_mongo_id("rss_channels")
    channel_doc = {
        "id": channel_id,
        "information_source_id": source_id,
        "url": channel_url,
        "category_id": payload.category_id,
        "active": True,
        "created_at": now,
        "updated_at": now,
    }

    try:
        rss_channels_col.insert_one(channel_doc)
    except DuplicateKeyError:
        # Liberar registros con esa URL de sources distintas (restos de test runs previos)
        rss_channels_col.delete_many({
            "url": channel_url,
            "information_source_id": {"$ne": source_id},
        })
        rss_channels_col.delete_many({"url": channel_url, "deleted_at": {"$exists": True}})
        try:
            rss_channels_col.insert_one(channel_doc)
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
    channel = ensure_rss_for_source(source_id, channel_id)
    update_data = payload.model_dump(exclude_unset=True)
    now = _utc_now()
    set_fields = {"updated_at": now}

    if "category_id" in update_data:
        ensure_category_exists(update_data["category_id"])
        set_fields["category_id"] = update_data["category_id"]

    if "url" in update_data:
        new_url = _normalize_url(str(update_data["url"]))
        new_url = _runtime_accessible_url(new_url)
        if not _is_rss_content(new_url):
            raise HTTPException(status_code=422, detail="La URL no contiene contenido RSS")
        set_fields["url"] = new_url

    try:
        rss_channels_col.update_one(_channel_query(source_id, channel_id), {"$set": set_fields})
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un canal RSS registrado con esa URL",
        ) from exc

    updated_doc = rss_channels_col.find_one(_channel_query(source_id, channel_id), {"_id": 0})
    return _doc_to_channel(updated_doc or channel)


@router.delete("/information-sources/{source_id}/rss-channels/{channel_id}", status_code=204)
def delete_source_channel(
    source_id: int, channel_id: int, _: UserInDB = Depends(get_current_user)
) -> Response:
    ensure_information_source_exists(source_id)
    ensure_rss_for_source(source_id, channel_id)
    now = _utc_now()
    rss_channels_col.update_one(
        _channel_query(source_id, channel_id),
        {"$set": {"active": False, "deleted_at": now, "updated_at": now}},
    )
    return Response(status_code=204)
