from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..dependencies import (
    es_token_valido,
    get_current_user,
    sanitize_user,
)
from ..store import (
    alerts_col,
    next_id,
    notifications_col,
    roles_store,
    users_col,
)
from .jwt_utils import create_access_token, hash_password, verify_password
from .user import (
    LoginRequest,
    Role,
    RoleCreate,
    RoleUpdate,
    TokenResponse,
    User,
    UserCreate,
    UserInDB,
    UserUpdate,
)

router = APIRouter()
ALLOWED_ROLE_NAMES = {"manager", "reader"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _doc_to_userindb(doc: dict) -> UserInDB:
    """Convierte un documento MongoDB en UserInDB eliminando el _id de Mongo."""
    doc = {k: v for k, v in doc.items() if k != "_id"}
    return UserInDB(**doc)


def ensure_role_ids_exist(role_ids: List[int]) -> None:
    """Valida que los IDs de rol enviados existan en el store de roles."""
    missing = [r for r in role_ids if r not in roles_store]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles no encontrados: {missing}",
        )

    invalid = [
        roles_store[role_id].name
        for role_id in role_ids
        if roles_store[role_id].name not in ALLOWED_ROLE_NAMES
    ]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles no permitidos: {invalid}",
        )


def ensure_role_name_allowed(role_name: str) -> None:
    """Valida que solo existan roles lector o gestor."""
    if role_name not in ALLOWED_ROLE_NAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol no permitido. Use 'reader' o 'manager'",
        )


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: LoginRequest) -> TokenResponse:
    """Autentica por email/password y devuelve JWT Bearer."""
    doc = users_col.find_one({"email": payload.email})
    if not doc or not verify_password(payload.password, doc.get("password_hash") or ""):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(doc["id"])
    return TokenResponse(access_token=token)


@router.post("/auth/register", response_model=TokenResponse, status_code=201, tags=["auth"])
def register(payload: UserCreate) -> TokenResponse:
    """Registra un usuario nuevo en MongoDB y devuelve un JWT para login automático."""
    if users_col.find_one({"email": payload.email}):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    if payload.role_ids:
        ensure_role_ids_exist(payload.role_ids)

    now = datetime.now(timezone.utc)
    user_id = next_id("users")
    users_col.insert_one({
        "id": user_id,
        "email": payload.email,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "organization": payload.organization,
        "role_ids": payload.role_ids,
        "password_hash": hash_password(payload.password),
        "created_at": now,
        "updated_at": now,
        "verification_token": str(uuid4()),
        "token_created_at": now,
        "role": "reader",
        "status": "active"
    })

    token = create_access_token(user_id)
    return TokenResponse(access_token=token)


@router.get("/auth/verify/{token}", tags=["auth"])
def verify_email(token: str):
    """Verifica la cuenta si el token no ha expirado."""
    doc = users_col.find_one({"verification_token": token})
    if not doc:
        raise HTTPException(status_code=404, detail="Token no válido")

    if not es_token_valido(doc.get("token_created_at")):
        raise HTTPException(status_code=400, detail="El enlace ha caducado (máximo 24h)")

    users_col.update_one(
        {"_id": doc["_id"]},
        {"$set": {"is_verified": True}, "$unset": {"verification_token": ""}},
    )
    return {"message": "Cuenta verificada correctamente"}


@router.post("/auth/forgot-password", tags=["auth"])
def forgot_password(payload: LoginRequest):
    """Genera token de recuperación de contraseña y lo almacena en MongoDB."""
    doc = users_col.find_one({"email": payload.email})
    if doc:
        reset_token = str(uuid4())
        users_col.update_one(
            {"email": payload.email},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_at": datetime.now(timezone.utc),
            }},
        )
        print(f"DEBUG: Token de recuperación para {payload.email}: {reset_token}")

    return {"message": "Si el email está registrado, recibirá instrucciones de recuperación"}


@router.post("/auth/reset-password", tags=["auth"])
def reset_password(token: str, new_password: str):
    """Restablece la contraseña validando el token y su caducidad de 24h."""
    doc = users_col.find_one({"reset_token": token})

    if not doc or not es_token_valido(doc.get("reset_token_at")):
        raise HTTPException(
            status_code=400,
            detail="El enlace es inválido o ha caducado (máximo 24h)",
        )

    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
    users_col.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {"password": hashed_pw},
            "$unset": {"reset_token": "", "reset_token_at": ""},
        },
    )
    return {"message": "Contraseña actualizada correctamente"}


# ---------------------------------------------------------------------------
# User routes
# ---------------------------------------------------------------------------

@router.get("/users", response_model=List[User], tags=["users"])
def list_users(_: UserInDB = Depends(get_current_user)) -> List[User]:
    """Lista usuarios sin exponer contraseñas."""
    return [sanitize_user(_doc_to_userindb(doc)) for doc in users_col.find()]


@router.post("/users", response_model=User, status_code=201, tags=["users"])
def create_user(payload: UserCreate, _: UserInDB = Depends(get_current_user)) -> User:
    """Crea usuario autenticado por token."""
    if users_col.find_one({"email": payload.email}):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    ensure_role_ids_exist(payload.role_ids)
    user_id = next_id("users")
    users_col.insert_one({"id": user_id, **payload.model_dump(), "is_verified": False})
    doc = users_col.find_one({"id": user_id})
    return sanitize_user(_doc_to_userindb(doc))


@router.get("/users/{user_id}", response_model=User, tags=["users"])
def get_user(user_id: int, _: UserInDB = Depends(get_current_user)) -> User:
    """Recupera un usuario por ID."""
    doc = users_col.find_one({"id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return sanitize_user(_doc_to_userindb(doc))


@router.put("/users/{user_id}", response_model=User, tags=["users"])
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
) -> User:
    """Actualiza el perfil con restricciones de seguridad; persiste en MongoDB."""
    is_manager = current_user.role == "manager" or any(
        roles_store[r_id].name == "manager"
        for r_id in current_user.role_ids
        if r_id in roles_store
    )
    if current_user.id != user_id and not is_manager:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este perfil")

    if not users_col.find_one({"id": user_id}):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if not is_manager:
        data.pop("role_ids", None)
        data.pop("email", None)

    if data:
        users_col.update_one({"id": user_id}, {"$set": data})

    updated = users_col.find_one({"id": user_id})
    return sanitize_user(_doc_to_userindb(updated))


@router.delete(
    "/users/{user_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["users"],
)
def delete_user(user_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina usuario y borra en cascada alertas y notificaciones asociadas."""
    if not users_col.find_one({"id": user_id}):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    alert_ids = [doc["id"] for doc in alerts_col.find({"user_id": user_id}, {"id": 1})]
    for alert_id in alert_ids:
        notifications_col.delete_many({"alert_id": alert_id})
    alerts_col.delete_many({"user_id": user_id})

    users_col.delete_one({"id": user_id})


# ---------------------------------------------------------------------------
# Role routes
# ---------------------------------------------------------------------------

@router.get("/roles", response_model=List[Role], tags=["roles"])
def list_roles(_: UserInDB = Depends(get_current_user)) -> List[Role]:
    """Lista todos los roles."""
    return list(roles_store.values())


@router.post("/roles", response_model=Role, status_code=201, tags=["roles"])
def create_role(payload: RoleCreate, _: UserInDB = Depends(get_current_user)) -> Role:
    """Crea un rol nuevo."""
    ensure_role_name_allowed(payload.name)
    role_id = next_id("roles")
    role = Role(id=role_id, **payload.model_dump())
    roles_store[role_id] = role
    return role


@router.get("/roles/{role_id}", response_model=Role, tags=["roles"])
def get_role(role_id: int, _: UserInDB = Depends(get_current_user)) -> Role:
    """Obtiene rol por ID."""
    role = roles_store.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


@router.put("/roles/{role_id}", response_model=Role, tags=["roles"])
def update_role(
    role_id: int,
    payload: RoleUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Role:
    """Actualiza los campos de un rol existente."""
    role = roles_store.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    update_data = payload.model_dump(exclude_unset=True)
    if "name" in update_data:
        ensure_role_name_allowed(update_data["name"])
    updated = role.model_copy(update=update_data)
    roles_store[role_id] = updated
    return updated


@router.delete(
    "/roles/{role_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["roles"],
)
def delete_role(role_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina rol si no está asignado a ningún usuario."""
    if role_id not in roles_store:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    assigned = users_col.find_one({"role_ids": role_id})
    if assigned:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar un rol asignado a usuarios",
        )

    roles_store.pop(role_id, None)
