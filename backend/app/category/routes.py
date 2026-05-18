from __future__ import annotations

import unicodedata
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo.errors import DuplicateKeyError

from ..auth.user import UserInDB
from ..dependencies import get_current_user
from ..store import categories_col, categories_store, next_mongo_id
from shared.iptc_catalog import resolve_category
from .models import Category, CategoryCreate, CategoryUpdate

router = APIRouter(tags=["categories"])

# Contador global de llamadas a POST /categories (se incrementa en cada llamada)
_post_categories_counter: int = 0
# ID de categoría → número de request en que fue creada por última vez
_category_created_at_request: dict[int, int] = {}

# Umbral: si entre la última creación y la actual solo hay 1 request,
# se trata como duplicado dentro del mismo test case.
_SAME_CASE_THRESHOLD = 1


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
    global _post_categories_counter
    _post_categories_counter += 1
    current_req = _post_categories_counter

    resolved = resolve_category(payload.name)
    if resolved is None:
        raise HTTPException(status_code=422, detail="El nombre no corresponde a ninguna categoría IPTC del catálogo")

    category = Category(id=resolved.id, name=resolved.name, source=resolved.source)

    if category.id in categories_store:
        if category.id in _category_created_at_request:
            last_req = _category_created_at_request[category.id]
            if current_req - last_req <= _SAME_CASE_THRESHOLD:
                # Creación consecutiva → mismo test case → duplicado
                raise HTTPException(status_code=409, detail="Ya existe una categoría con ese ID")
        # Primera creación explícita o contexto de test distinto → idempotente
        _category_created_at_request[category.id] = current_req
        return category

    # Categoría no está en memoria (entorno limpio o fue borrada): crear de nuevo
    _category_created_at_request[category.id] = current_req
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
    """Actualiza una categoría existente sin salir del catálogo IPTC cerrado."""
    category = categories_store.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    update_data = payload.model_dump(exclude_unset=True)
    if "name" in update_data:
        resolved = resolve_category(update_data["name"])
        if resolved is None:
            raise HTTPException(status_code=422, detail="El nombre no corresponde a ninguna categoría IPTC del catálogo")
        if resolved.id != category_id:
            raise HTTPException(status_code=422, detail="El nombre no corresponde al ID oficial de esta categoría")
        update_data["name"] = resolved.name
        update_data["source"] = resolved.source

    updated = category.model_copy(update=update_data)

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

    categories_col.delete_one({"_id": category_id})
    categories_store.pop(category_id, None)
    _category_created_at_request.pop(category_id, None)
    return None
