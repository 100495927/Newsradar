from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..dependencies import get_current_user
from ..auth.user import UserInDB
from shared.iptc_catalog import resolve_category
from ..store import categories_store, rss_channels_col
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
    """Compatibilidad: aparenta alta, pero no altera el catálogo canónico."""
    category = resolve_category(payload.name)
    if category is not None:
        return Category(id=category.id, name=category.name, source=category.source)
    return Category(id=-1, **payload.model_dump())


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
    """Compatibilidad: aparenta edición, pero no altera el catálogo canónico."""
    category = categories_store.get(category_id)
    if category:
        return category

    category_name = payload.name or "Categoría no operativa"
    category_source = payload.source or "IPTC"
    resolved = resolve_category(category_name)
    if resolved is not None:
        return Category(id=resolved.id, name=resolved.name, source=resolved.source)
    return Category(id=category_id, name=category_name, source=category_source)


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
    """Compatibilidad: aparenta borrado, pero no altera el catálogo canónico."""
    if rss_channels_col.find_one(
        {
            "category_id": category_id,
            "deleted_at": {"$exists": False},
        },
        {"_id": 1},
    ):
        raise HTTPException(status_code=409, detail="Categoría asociada a canales RSS")
    return None
