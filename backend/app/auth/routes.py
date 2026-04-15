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
    active_tokens,
    alerts_store,
    next_id,
    notifications_store,
    roles_store,
    users_col,
    users_store,
)
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_role_ids_exist(role_ids: List[int]) -> None:
    """Valida que los IDs de rol enviados existan en el store de roles."""
    missing = [r for r in role_ids if r not in roles_store]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles no encontrados: {missing}",
        )


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: LoginRequest) -> TokenResponse:
    """Autentica por email/password y devuelve token Bearer temporal."""
    user = next((u for u in users_store.values() if u.email == payload.email), None)
    if user is None or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = str(uuid4())
    active_tokens[token] = user.id
    return TokenResponse(access_token=token)


@router.post("/auth/register", response_model=User, status_code=201, tags=["auth"])
def register(payload: UserCreate) -> User:
    """Registra un usuario nuevo validando email único y roles existentes."""
    if any(u.email == payload.email for u in users_store.values()):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    ensure_role_ids_exist(payload.role_ids)

    user_id = next_id("users")
    user_db = UserInDB(
        id=user_id,
        verification_token=str(uuid4()),
        token_created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    users_store[user_id] = user_db
    print(f"DEBUG: Token para {user_db.email}: {user_db.verification_token}")
    return sanitize_user(user_db)


@router.get("/auth/verify/{token}", tags=["auth"])
def verify_email(token: str):
    """Verifica la cuenta si el token no ha expirado."""
    user = next((u for u in users_store.values() if u.verification_token == token), None)

    if not user:
        raise HTTPException(status_code=404, detail="Token no válido")

    if not es_token_valido(user.token_created_at):
        raise HTTPException(status_code=400, detail="El enlace ha caducado (máximo 24h)")

    user.is_verified = True
    user.verification_token = None
    return {"message": "Cuenta verificada correctamente"}


@router.post("/auth/forgot-password", tags=["auth"])
def forgot_password(payload: LoginRequest):
    """Genera token de recuperación de contraseña y lo almacena en MongoDB."""
    user = users_col.find_one({"email": payload.email})

    if user:
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
    user_data = users_col.find_one({"reset_token": token})

    if not user_data or not es_token_valido(user_data.get("reset_token_at")):
        raise HTTPException(
            status_code=400,
            detail="El enlace es inválido o ha caducado (máximo 24h)",
        )

    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
    users_col.update_one(
        {"id": user_data["id"]},
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
    return [sanitize_user(u) for u in users_store.values()]


@router.post("/users", response_model=User, status_code=201, tags=["users"])
def create_user(payload: UserCreate, _: UserInDB = Depends(get_current_user)) -> User:
    """Crea usuario administrativo autenticado por token."""
    if any(u.email == payload.email for u in users_store.values()):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    ensure_role_ids_exist(payload.role_ids)
    user_id = next_id("users")
    user_db = UserInDB(id=user_id, **payload.model_dump())
    users_store[user_id] = user_db
    return sanitize_user(user_db)


@router.get("/users/{user_id}", response_model=User, tags=["users"])
def get_user(user_id: int, _: UserInDB = Depends(get_current_user)) -> User:
    """Recupera un usuario por ID."""
    user = users_store.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return sanitize_user(user)


@router.put("/users/{user_id}", response_model=User, tags=["users"])
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
) -> User:
    """Actualiza el perfil con restricciones de seguridad; persiste en MongoDB."""
    is_admin = any(
        roles_store[r_id].name == "admin"
        for r_id in current_user.role_ids
        if r_id in roles_store
    )
    if current_user.id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este perfil")

    user_data = users_col.find_one({"id": user_id})
    if not user_data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if not is_admin:
        data.pop("role_ids", None)
        data.pop("email", None)

    if data:
        users_col.update_one({"id": user_id}, {"$set": data})

    updated = users_col.find_one({"id": user_id})
    return sanitize_user(UserInDB(**updated))


@router.delete(
    "/users/{user_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["users"],
)
def delete_user(user_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina usuario y borra en cascada alertas y notificaciones asociadas."""
    if user_id not in users_store:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    alert_ids = [a.id for a in alerts_store.values() if a.user_id == user_id]
    for alert_id in alert_ids:
        notification_ids = [n.id for n in notifications_store.values() if n.alert_id == alert_id]
        for nid in notification_ids:
            notifications_store.pop(nid, None)
        alerts_store.pop(alert_id, None)

    users_store.pop(user_id, None)


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
    updated = role.model_copy(update=payload.model_dump(exclude_unset=True))
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

    for user in users_store.values():
        if role_id in user.role_ids:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar un rol asignado a usuarios",
            )

    roles_store.pop(role_id, None)
