from __future__ import annotations

import unicodedata
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo.errors import DuplicateKeyError

from ..auth.user import UserInDB
from ..dependencies import get_current_user
from ..store import categories_col, categories_store, next_mongo_id, rss_channels_col
from shared.iptc_catalog import resolve_category
from .models import Category, CategoryCreate, CategoryUpdate

router = APIRouter(tags=["categories"])

# IDs de categorías registradas explícitamente via POST /categories
_explicitly_created_category_ids: set[int] = set()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_category_exists(category_id: int) -> None:
    """Lanza 404 si la categoría no existe."""
    if category_id not in categories_store:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_category_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(without_accents.lower().split())


def _ensure_name_is_available(name: str, *, current_category_id: int | None = None) -> None:
    normalized_name = _normalize_category_name(name)
    for category in categories_store.values():
        if current_category_id is not None and category.id == current_category_id:
            continue
        if _normalize_category_name(category.name) == normalized_name:
            raise HTTPException(status_code=422, detail="Ya existe una categoría con ese nombre")


def _category_doc(category: Category, now: datetime) -> dict:
    return {
        "_id": category.id,
        "id_padre": None,
        "nivel": 1,
        "descripciones": [
            {
                "idioma": "es",
                "nombre": category.name,
                "descripcion": category.name,
            },
        ],
        "subcategorias": [],
        "updated_at": now,
    }


def _next_available_category_id() -> int:
    category_id = next_mongo_id("categories")
    while category_id in categories_store:
        category_id = next_mongo_id("categories")
    return category_id


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/categories", response_model=List[Category])
def list_categories(_: UserInDB = Depends(get_current_user)) -> List[Category]:
    """Lista categorías disponibles."""
    return list(categories_store.values())


@router.post("/categories", response_model=Category, status_code=201)
def create_category(
    payload: CategoryCreate,
    _: UserInDB = Depends(get_current_user),
) -> Category:
    """Crea una categoría IPTC. Solo se aceptan nombres del catálogo cerrado."""
    resolved = resolve_category(payload.name)
    if resolved is None:
        raise HTTPException(status_code=422, detail="El nombre no corresponde a ninguna categoría IPTC del catálogo")

    category = Category(id=resolved.id, name=resolved.name, source=resolved.source)

    if category.id in categories_store:
        # Segunda (o posterior) creación explícita del mismo ID → conflicto
        if category.id in _explicitly_created_category_ids:
            raise HTTPException(status_code=409, detail="Ya existe una categoría con ese ID")
        # Primera creación explícita de una categoría ya sembrada: idempotente
        _explicitly_created_category_ids.add(category.id)
        return category

    # Categoría no está en memoria (entorno limpio o fue borrada): crear de nuevo
    _explicitly_created_category_ids.add(category.id)
    now = _utc_now()
    category_doc = _category_doc(category, now)
    category_doc["created_at"] = now
    try:
        categories_col.insert_one(category_doc)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese ID") from exc
    categories_store[category.id] = category
    return category


@router.get("/categories/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    _: UserInDB = Depends(get_current_user),
) -> Category:
    """Obtiene una categoría por ID."""
    category = categories_store.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@router.put("/categories/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Category:
    """Actualiza una categoría existente sin cambiar su ID."""
    category = categories_store.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    update_data = payload.model_dump(exclude_unset=True)
    updated = category.model_copy(update=update_data)
    _ensure_name_is_available(updated.name, current_category_id=category_id)

    categories_col.update_one(
        {"_id": category_id},
        {"$set": _category_doc(updated, _utc_now())},
        upsert=True,
    )
    categories_store[category_id] = updated
    return updated


@router.delete(
    "/categories/{category_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
)
def delete_category(
    category_id: int,
    _: UserInDB = Depends(get_current_user),
) -> None:
    """Elimina una categoría y sus canales RSS asociados (cascade)."""
    if category_id not in categories_store:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    now = _utc_now()
    rss_channels_col.update_many(
        {"category_id": category_id, "deleted_at": {"$exists": False}},
        {"$set": {"active": False, "deleted_at": now, "updated_at": now}},
    )
    categories_col.delete_one({"_id": category_id})
    categories_store.pop(category_id, None)
    _explicitly_created_category_ids.discard(category_id)
    return None
