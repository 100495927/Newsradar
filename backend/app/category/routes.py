from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..dependencies import get_current_user
from ..auth.user import UserInDB
from ..store import categories_store, next_id, rss_channels_store
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

    for channel in rss_channels_store.values():
        if channel.category_id == category_id:
            raise HTTPException(status_code=409, detail="Categoría asociada a canales RSS")

    categories_store.pop(category_id, None)
