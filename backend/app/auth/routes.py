from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

import pymongo
from fastapi import APIRouter, Depends, HTTPException, Response

from ..dependencies import (
    es_token_valido,
    get_current_user,
    normalize_legacy_user_doc,
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
from shared.utils import send_notification_email_with_error


def _frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:5173")

router = APIRouter()
ROLELESS_DEFAULT_ROLE_ID = 1
ROLELESS_DEFAULT_ROLE_NAME = "manager"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _doc_to_userindb(doc: dict) -> UserInDB:
    """Convierte un documento MongoDB en UserInDB eliminando el _id de Mongo."""
    doc = normalize_legacy_user_doc(doc)
    return UserInDB(**doc)


def _sync_user_counter_from_mongo() -> None:
    """Evita IDs duplicados cuando el contador en memoria arranca desfasado."""
    max_doc = users_col.find_one(sort=[("id", pymongo.DESCENDING)])
    if max_doc and isinstance(max_doc.get("id"), int):
        from .. import store

        store.counters["users"] = max(store.counters["users"], max_doc["id"] + 1)


def _ensure_manager_role() -> Role:
    """Garantiza un rol canonico de gestor para compatibilidad del contrato."""
    role = roles_store.get(ROLELESS_DEFAULT_ROLE_ID)
    if isinstance(role, Role) and role.name == ROLELESS_DEFAULT_ROLE_NAME:
        return role

    canonical_role = Role(id=ROLELESS_DEFAULT_ROLE_ID, name=ROLELESS_DEFAULT_ROLE_NAME)
    roles_store[ROLELESS_DEFAULT_ROLE_ID] = canonical_role
    return canonical_role


def _default_role_ids() -> list[int]:
    return [_ensure_manager_role().id]


def ensure_role_ids_exist(role_ids: List[int]) -> None:
    """Se acepta por compatibilidad, pero ya no condiciona nada."""
    return None


def ensure_role_name_allowed(role_name: str) -> None:
    """Los endpoints de roles se normalizan a gestor sin restricciones funcionales."""
    return None


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: LoginRequest) -> TokenResponse:
    """Autentica por email/password y devuelve JWT Bearer."""
    doc = users_col.find_one({"email": payload.email})
    if not doc or not verify_password(payload.password, doc.get("password_hash") or ""):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Bloquear usuarios nuevos que aún no han verificado su correo.
    # Los usuarios legacy (is_verified=None) pueden seguir accediendo.
    if doc.get("is_verified") is False:
        raise HTTPException(
            status_code=403,
            detail="Debes verificar tu correo electrónico antes de iniciar sesión. Revisa tu bandeja de entrada.",
        )

    token = create_access_token(doc["id"])
    return TokenResponse(access_token=token)


@router.post("/auth/register", response_model=User, status_code=201, tags=["auth"])
def register(payload: UserCreate) -> User:
    """Registra un usuario nuevo, envía email de verificación y devuelve el perfil público."""
    if users_col.find_one({"email": payload.email}):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    _sync_user_counter_from_mongo()
    now = datetime.now(timezone.utc)
    user_id = next_id("users")
    role_ids = _default_role_ids()
    verification_token = str(uuid4())

    users_col.insert_one({
        "id": user_id,
        "email": payload.email,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "organization": payload.organization,
        "role_ids": role_ids,
        "password_hash": hash_password(payload.password),
        "created_at": now,
        "updated_at": now,
        "verification_token": verification_token,
        "token_created_at": now,
        "role": ROLELESS_DEFAULT_ROLE_NAME,
        "status": "active",
        "is_verified": False,
    })

    verify_link = f"{_frontend_url()}/verify/{verification_token}"
    subject = "NewsRadar – Verifica tu cuenta"
    body = (
        f"Hola {payload.first_name},\n\n"
        f"Gracias por registrarte en NewsRadar.\n\n"
        f"Haz clic en el siguiente enlace para verificar tu cuenta "
        f"(válido durante 24 horas):\n\n"
        f"{verify_link}\n\n"
        f"Si no has creado esta cuenta, ignora este mensaje.\n\n"
        f"— El equipo de NewsRadar"
    )
    sent, error = send_notification_email_with_error(payload.email, subject, body)
    if not sent:
        # Registramos el fallo pero no bloqueamos el registro; el admin puede reenviar manualmente.
        import logging
        logging.getLogger(__name__).warning(
            "No se pudo enviar el email de verificación a %s: %s", payload.email, error
        )

    doc = users_col.find_one({"id": user_id})
    return sanitize_user(_doc_to_userindb(doc))


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
    """Genera token de recuperación de contraseña y envía el email al usuario."""
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
        reset_link = f"{_frontend_url()}/reset-password?token={reset_token}"
        subject = "NewsRadar – Recuperación de contraseña"
        body = (
            f"Hola,\n\n"
            f"Hemos recibido una solicitud para restablecer la contraseña de tu cuenta "
            f"en NewsRadar ({payload.email}).\n\n"
            f"Haz clic en el siguiente enlace para crear una nueva contraseña "
            f"(válido durante 24 horas):\n\n"
            f"{reset_link}\n\n"
            f"Si no solicitaste este cambio, ignora este mensaje.\n\n"
            f"— El equipo de NewsRadar"
        )
        sent, error = send_notification_email_with_error(payload.email, subject, body)
        if not sent:
            import logging
            logging.getLogger(__name__).warning(
                "No se pudo enviar el email de recuperación a %s: %s", payload.email, error
            )

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

    users_col.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {"password_hash": hash_password(new_password)},
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

    _sync_user_counter_from_mongo()
    now = datetime.now(timezone.utc)
    user_id = next_id("users")
    users_col.insert_one(
        {
            "id": user_id,
            "email": payload.email,
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "organization": payload.organization,
            "role_ids": _default_role_ids(),
            "password_hash": hash_password(payload.password),
            "created_at": now,
            "updated_at": now,
            "role": ROLELESS_DEFAULT_ROLE_NAME,
            "status": "active",
            "is_verified": False,
        }
    )
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
    """Actualiza el propio perfil; la logica de roles ya no altera permisos."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este perfil")

    if not users_col.find_one({"id": user_id}):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)
    data.pop("role_ids", None)
    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))

    if data:
        data["updated_at"] = datetime.now(timezone.utc)
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
    """Expone un unico rol canonico sin efecto funcional."""
    return [_ensure_manager_role()]


@router.post("/roles", response_model=Role, status_code=201, tags=["roles"])
def create_role(payload: RoleCreate, _: UserInDB = Depends(get_current_user)) -> Role:
    """Acepta la operacion por compatibilidad, normalizando siempre a gestor."""
    ensure_role_name_allowed(payload.name)
    return _ensure_manager_role()


@router.get("/roles/{role_id}", response_model=Role, tags=["roles"])
def get_role(role_id: int, _: UserInDB = Depends(get_current_user)) -> Role:
    """Responde satisfactoriamente para cualquier role_id sin efectos laterales."""
    _ensure_manager_role()
    return Role(id=role_id, name=ROLELESS_DEFAULT_ROLE_NAME)


@router.put("/roles/{role_id}", response_model=Role, tags=["roles"])
def update_role(
    role_id: int,
    payload: RoleUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Role:
    """Acepta la operacion por compatibilidad sin modificar el backend."""
    if payload.name is not None:
        ensure_role_name_allowed(payload.name)
    _ensure_manager_role()
    return Role(id=role_id, name=ROLELESS_DEFAULT_ROLE_NAME)


@router.delete(
    "/roles/{role_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["roles"],
)
def delete_role(role_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Acepta el borrado por compatibilidad sin tocar permisos ni persistencia."""
    _ensure_manager_role()
