from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import categories_store, next_id, rss_fuentes_col
from .models import Category, CategoryCreate, CategoryUpdate

router = APIRouter(tags=["categories"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_category_exists(category_id: int) -> None:
    """Lanza 404 si la categoría no existe."""
    if category_id not in categories_store:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


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
    """Crea una categoría (fuente IPTC en este prototipo)."""
    category_id = next_id("categories")
    category = Category(id=category_id, **payload.model_dump())
    categories_store[category_id] = category
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
    """Actualiza una categoría existente."""
    category = categories_store.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    updated = category.model_copy(update=payload.model_dump(exclude_unset=True))
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
    """Elimina categoría solo si no está asociada a canales RSS."""
    if category_id not in categories_store:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    linked_channel = rss_fuentes_col.find_one(
        {
            "tipo": "channel",
            "category_id": category_id,
            "deleted_at": {"$exists": False},
        },
        {"_id": 1},
    )
    if linked_channel:
        raise HTTPException(status_code=409, detail="Categoría asociada a canales RSS")

    categories_store.pop(category_id, None)
