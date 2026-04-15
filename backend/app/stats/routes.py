from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import next_id, stats_store
from .models import Stats, StatsCreate, StatsUpdate

router = APIRouter(tags=["stats"])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=List[Stats])
def list_stats(_: UserInDB = Depends(get_current_user)) -> List[Stats]:
    """Lista registros de estadísticas."""
    return list(stats_store.values())


@router.post("/stats", response_model=Stats, status_code=201)
def create_stats(
    payload: StatsCreate,
    _: UserInDB = Depends(get_current_user),
) -> Stats:
    """Crea un registro de estadísticas."""
    stats_id = next_id("stats")
    stats = Stats(id=stats_id, **payload.model_dump())
    stats_store[stats_id] = stats
    return stats


@router.get("/stats/{stats_id}", response_model=Stats)
def get_stats(
    stats_id: int,
    _: UserInDB = Depends(get_current_user),
) -> Stats:
    """Obtiene un registro de estadísticas por ID."""
    stats = stats_store.get(stats_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    return stats


@router.put("/stats/{stats_id}", response_model=Stats)
def update_stats(
    stats_id: int,
    payload: StatsUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Stats:
    """Actualiza un registro de estadísticas."""
    stats = stats_store.get(stats_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    updated = stats.model_copy(update=payload.model_dump(exclude_unset=True))
    stats_store[stats_id] = updated
    return updated


@router.delete(
    "/stats/{stats_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
)
def delete_stats(
    stats_id: int,
    _: UserInDB = Depends(get_current_user),
) -> None:
    """Elimina un registro de estadísticas."""
    if stats_id not in stats_store:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    stats_store.pop(stats_id, None)
