from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response

from ..category.routes import ensure_category_exists
from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import next_id, sources_col, channels_col
from .models import (
    InformationSource,
    InformationSourceCreate,
    InformationSourceUpdate,
    RSSChannel,
    RSSChannelCreate,
    RSSChannelUpdate,
)

router = APIRouter(tags=["information-sources", "rss-channels"])

# ---------------------------------------------------------------------------
# Helpers (Ahora consultan MongoDB)
# ---------------------------------------------------------------------------

def ensure_information_source_exists(source_id: int) -> dict:
    """Lanza 404 si la fuente de información no existe en MongoDB."""
    source = sources_col.find_one({"id": source_id}, {"_id": 0})
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    return source

def ensure_rss_for_source(source_id: int, channel_id: int) -> dict:
    """Valida que el canal RSS exista y pertenezca a la fuente en MongoDB."""
    channel = channels_col.find_one({"id": channel_id, "information_source_id": source_id}, {"_id": 0})
    if not channel:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    return channel

# ---------------------------------------------------------------------------
# Information Source routes
# ---------------------------------------------------------------------------

@router.get("/information-sources", response_model=List[InformationSource])
def list_information_sources(_: UserInDB = Depends(get_current_user)) -> List[InformationSource]:
    """Lista fuentes de información registradas en Mongo."""
    cursor = sources_col.find({}, {"_id": 0})
    return [InformationSource(**doc) for doc in cursor]

@router.post("/information-sources", response_model=InformationSource, status_code=201)
def create_information_source(
    payload: InformationSourceCreate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    """Registra una nueva fuente en MongoDB."""
    source_id = next_id("information_sources")
    new_source = {
        "id": source_id,
        "name": payload.name,
        "url": str(payload.url)
    }
    sources_col.insert_one(new_source)
    return InformationSource(**new_source)

@router.get("/information-sources/{source_id}", response_model=InformationSource)
def get_information_source(source_id: int, _: UserInDB = Depends(get_current_user)) -> InformationSource:
    """Obtiene una fuente de información por ID."""
    source = ensure_information_source_exists(source_id)
    return InformationSource(**source)

@router.put("/information-sources/{source_id}", response_model=InformationSource)
def update_information_source(
    source_id: int,
    payload: InformationSourceUpdate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    """Actualiza una fuente de información en Mongo."""
    ensure_information_source_exists(source_id)
    update_data = payload.model_dump(exclude_unset=True)
    
    if "url" in update_data:
        update_data["url"] = str(update_data["url"])

    sources_col.update_one({"id": source_id}, {"$set": update_data})
    updated_doc = sources_col.find_one({"id": source_id}, {"_id": 0})
    return InformationSource(**updated_doc)

@router.delete("/information-sources/{source_id}", status_code=204)
def delete_information_source(source_id: int, _: UserInDB = Depends(get_current_user)):
    """Elimina una fuente y borra en cascada sus canales RSS."""
    ensure_information_source_exists(source_id)
    channels_col.delete_many({"information_source_id": source_id})
    sources_col.delete_one({"id": source_id})
    return Response(status_code=204)

# ---------------------------------------------------------------------------
# RSS Channel routes
# ---------------------------------------------------------------------------

@router.get("/information-sources/{source_id}/rss-channels", response_model=List[RSSChannel])
def list_source_channels(source_id: int, _: UserInDB = Depends(get_current_user)) -> List[RSSChannel]:
    """Lista canales RSS asociados a una fuente desde Mongo."""
    ensure_information_source_exists(source_id)
    cursor = channels_col.find({"information_source_id": source_id}, {"_id": 0})
    return [RSSChannel(**doc) for doc in cursor]

@router.post("/information-sources/{source_id}/rss-channels", response_model=RSSChannel, status_code=201)
def create_source_channel(
    source_id: int,
    payload: RSSChannelCreate,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    """Crea un canal RSS validando la categoría en Mongo."""
    ensure_information_source_exists(source_id)
    ensure_category_exists(payload.category_id)

    channel_id = next_id("rss_channels")
    new_channel = {
        "id": channel_id,
        "information_source_id": source_id,
        "url": str(payload.url),
        "category_id": payload.category_id
    }
    channels_col.insert_one(new_channel)
    return RSSChannel(**new_channel)

@router.get("/information-sources/{source_id}/rss-channels/{channel_id}", response_model=RSSChannel)
def get_source_channel(source_id: int, channel_id: int, _: UserInDB = Depends(get_current_user)) -> RSSChannel:
    """Recupera un canal RSS concreto de una fuente."""
    ensure_information_source_exists(source_id)
    channel = ensure_rss_for_source(source_id, channel_id)
    return RSSChannel(**channel)

@router.put("/information-sources/{source_id}/rss-channels/{channel_id}", response_model=RSSChannel)
def update_source_channel(
    source_id: int,
    channel_id: int,
    payload: RSSChannelUpdate,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    """Actualiza un canal RSS y valida categoría si cambia."""
    ensure_information_source_exists(source_id)
    ensure_rss_for_source(source_id, channel_id)

    update_data = payload.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        ensure_category_exists(update_data["category_id"])
    
    if "url" in update_data:
        update_data["url"] = str(update_data["url"])

    channels_col.update_one({"id": channel_id}, {"$set": update_data})
    updated_doc = channels_col.find_one({"id": channel_id}, {"_id": 0})
    return RSSChannel(**updated_doc)

@router.delete("/information-sources/{source_id}/rss-channels/{channel_id}", status_code=204)
def delete_source_channel(source_id: int, channel_id: int, _: UserInDB = Depends(get_current_user)):
    """Elimina un canal RSS de una fuente."""
    ensure_information_source_exists(source_id)
    ensure_rss_for_source(source_id, channel_id)
    channels_col.delete_one({"id": channel_id})
    return Response(status_code=204)
