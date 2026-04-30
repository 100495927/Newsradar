from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response

from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import next_id, stats_col
from .models import FeedStats, GlobalDashboard, Stats, StatsCreate, StatsUpdate, TimelineEntry, WordCloudItem
from . import service

router = APIRouter(tags=["stats"])

# ---------------------------------------------------------------------------
# Dashboard / analytics routes must be registered BEFORE /{stats_id} so
# FastAPI does not try to coerce "global" / "timeline" etc. to int.
# ---------------------------------------------------------------------------

@router.get("/global", response_model=GlobalDashboard)
def read_global_stats(_: UserInDB = Depends(get_current_user)):
    """Panel de mando con estadísticas globales."""
    return service.get_global_stats()


@router.get("/timeline", response_model=List[TimelineEntry])
def read_timeline(_: UserInDB = Depends(get_current_user)):
    """Noticias capturadas por día (últimos 30 días)."""
    return service.get_timeline_stats()


@router.get("/feed/{feed_id}", response_model=FeedStats)
def read_feed_stats(feed_id: int, _: UserInDB = Depends(get_current_user)):
    """Estadísticas específicas para un canal RSS."""
    return service.get_feed_stats(feed_id)


@router.get("/cloud/{categoria}", response_model=List[WordCloudItem])
def read_word_cloud(categoria: str, _: UserInDB = Depends(get_current_user)):
    """Nube de palabras por categoría."""
    return service.get_word_cloud_data(categoria)



# ---------------------------------------------------------------------------
# CRUD contract routes (api_ag_comentado.py)
# /{stats_id} is last so literal path segments above take priority.
# ---------------------------------------------------------------------------

@router.get("", response_model=List[Stats])
def list_stats(_: UserInDB = Depends(get_current_user)) -> List[Stats]:
    """Lista registros de estadísticas desde MongoDB."""
    cursor = stats_col.find({}, {"_id": 0})
    return [Stats(**doc) for doc in cursor]


@router.post("", response_model=Stats, status_code=201)
def create_stats(
    payload: StatsCreate,
    _: UserInDB = Depends(get_current_user),
) -> Stats:
    """Crea un registro de estadísticas en MongoDB."""
    stats_id = next_id("stats")
    new_stats = {
        "id": stats_id,
        "metrics": [m.model_dump() for m in payload.metrics]
    }
    stats_col.insert_one(new_stats)
    return Stats(**new_stats)


@router.get("/{stats_id}", response_model=Stats)
def get_stats(
    stats_id: int,
    _: UserInDB = Depends(get_current_user),
) -> Stats:
    """Obtiene un registro de estadísticas por ID."""
    stats = stats_col.find_one({"id": stats_id}, {"_id": 0})
    if not stats:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    return Stats(**stats)


@router.put("/{stats_id}", response_model=Stats)
def update_stats(
    stats_id: int,
    payload: StatsUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Stats:
    """Actualiza un registro de estadísticas en MongoDB."""
    stats_exists = stats_col.find_one({"id": stats_id})
    if not stats_exists:
        raise HTTPException(status_code=404, detail="Stats no encontrados")

    update_data = payload.model_dump(exclude_unset=True)
    if "metrics" in update_data:
        update_data["metrics"] = [
            m.model_dump() if hasattr(m, "model_dump") else m
            for m in update_data["metrics"]
        ]

    stats_col.update_one({"id": stats_id}, {"$set": update_data})
    updated_doc = stats_col.find_one({"id": stats_id}, {"_id": 0})
    return Stats(**updated_doc)


@router.delete("/{stats_id}", status_code=204)
def delete_stats(
    stats_id: int,
    _: UserInDB = Depends(get_current_user),
) -> Response:
    """Elimina un registro de estadísticas de MongoDB."""
    result = stats_col.delete_one({"id": stats_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    return Response(status_code=204)
