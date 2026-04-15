from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..category.routes import ensure_category_exists
from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import information_sources_store, next_id, rss_channels_store
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
# Helpers
# ---------------------------------------------------------------------------

def ensure_information_source_exists(source_id: int) -> None:
    """Lanza 404 si la fuente de información no existe."""
    if source_id not in information_sources_store:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")


def ensure_rss_for_source(source_id: int, channel_id: int) -> RSSChannel:
    """Valida que el canal RSS exista y cuelgue de la fuente indicada."""
    channel = rss_channels_store.get(channel_id)
    if not channel or channel.information_source_id != source_id:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    return channel


# ---------------------------------------------------------------------------
# Information Source routes
# ---------------------------------------------------------------------------

@router.get("/information-sources", response_model=List[InformationSource])
def list_information_sources(
    _: UserInDB = Depends(get_current_user),
) -> List[InformationSource]:
    """Lista fuentes de información registradas."""
    return list(information_sources_store.values())


@router.post("/information-sources", response_model=InformationSource, status_code=201)
def create_information_source(
    payload: InformationSourceCreate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    """Crea una fuente de información."""
    source_id = next_id("information_sources")
    source = InformationSource(id=source_id, **payload.model_dump())
    information_sources_store[source_id] = source
    return source


@router.get("/information-sources/{source_id}", response_model=InformationSource)
def get_information_source(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    """Obtiene una fuente de información por ID."""
    source = information_sources_store.get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    return source


@router.put("/information-sources/{source_id}", response_model=InformationSource)
def update_information_source(
    source_id: int,
    payload: InformationSourceUpdate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    """Actualiza una fuente de información."""
    source = information_sources_store.get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    updated = source.model_copy(update=payload.model_dump(exclude_unset=True))
    information_sources_store[source_id] = updated
    return updated


@router.delete(
    "/information-sources/{source_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
)
def delete_information_source(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
) -> None:
    """Elimina una fuente y borra en cascada sus canales RSS."""
    if source_id not in information_sources_store:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")

    channel_ids = [
        ch.id
        for ch in rss_channels_store.values()
        if ch.information_source_id == source_id
    ]
    for channel_id in channel_ids:
        rss_channels_store.pop(channel_id, None)

    information_sources_store.pop(source_id, None)


# ---------------------------------------------------------------------------
# RSS Channel routes
# ---------------------------------------------------------------------------

@router.get(
    "/information-sources/{source_id}/rss-channels",
    response_model=List[RSSChannel],
)
def list_source_channels(
    source_id: int,
    _: UserInDB = Depends(get_current_user),
) -> List[RSSChannel]:
    """Lista canales RSS asociados a una fuente."""
    ensure_information_source_exists(source_id)
    return [ch for ch in rss_channels_store.values() if ch.information_source_id == source_id]


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
    """Crea un canal RSS para una fuente validando la categoría."""
    ensure_information_source_exists(source_id)
    ensure_category_exists(payload.category_id)

    channel_id = next_id("rss_channels")
    channel = RSSChannel(
        id=channel_id,
        information_source_id=source_id,
        **payload.model_dump(),
    )
    rss_channels_store[channel_id] = channel
    return channel


@router.get(
    "/information-sources/{source_id}/rss-channels/{channel_id}",
    response_model=RSSChannel,
)
def get_source_channel(
    source_id: int,
    channel_id: int,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    """Recupera un canal RSS concreto de una fuente."""
    ensure_information_source_exists(source_id)
    return ensure_rss_for_source(source_id, channel_id)


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
    """Actualiza un canal RSS y valida categoría si cambia."""
    ensure_information_source_exists(source_id)
    channel = ensure_rss_for_source(source_id, channel_id)

    update_data = payload.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        ensure_category_exists(update_data["category_id"])

    updated = channel.model_copy(update=update_data)
    rss_channels_store[channel_id] = updated
    return updated


@router.delete(
    "/information-sources/{source_id}/rss-channels/{channel_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
)
def delete_source_channel(
    source_id: int,
    channel_id: int,
    _: UserInDB = Depends(get_current_user),
) -> None:
    """Elimina un canal RSS de una fuente."""
    ensure_information_source_exists(source_id)
    ensure_rss_for_source(source_id, channel_id)
    rss_channels_store.pop(channel_id, None)
