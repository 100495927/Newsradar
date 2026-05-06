from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from .auth.jwt_utils import decode_access_token
from .auth.user import User, UserInDB
from .store import users_col

security = HTTPBearer(auto_error=False)

LEGACY_DEFAULT_EMAILS = {
    "AdminDefault@newsradar.local": "AdminDefault@newsradar.com",
    "GestorDefault@newsradar.local": "GestorDefault@newsradar.com",
    "LectorDefault@newsradar.local": "LectorDefault@newsradar.com",
}


def normalize_legacy_user_doc(doc: dict) -> dict:
    """Migra en lectura los usuarios semilla antiguos con email .local."""
    normalized_doc = {k: v for k, v in doc.items() if k != "_id"}
    legacy_email = normalized_doc.get("email")
    canonical_email = LEGACY_DEFAULT_EMAILS.get(legacy_email)
    if canonical_email:
        normalized_doc["email"] = canonical_email
        users_col.update_one(
            {"id": normalized_doc["id"], "email": legacy_email},
            {"$set": {"email": canonical_email}},
        )
    return normalized_doc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInDB:
    """Resuelve el usuario autenticado validando el JWT y consultando MongoDB."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Token inválido o ausente")

    try:
        user_id = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    doc = users_col.find_one({"id": user_id})
    if not doc:
        raise HTTPException(status_code=401, detail="Usuario inválido")

    doc = normalize_legacy_user_doc(doc)
    return UserInDB(**doc)


def sanitize_user(user: UserInDB) -> User:
    """Devuelve la vista pública del usuario sin password."""
    return User(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=user.organization,
        role_ids=user.role_ids,
    )


def user_has_manager_role(user: UserInDB) -> bool:
    """La logica de roles esta desactivada: todo usuario autenticado opera como gestor."""
    return True


def ensure_user_can_access(target_user_id: int, user: UserInDB) -> None:
    """Permite acceso solo al propio usuario para evitar privilegios transversales."""
    if user.id == target_user_id:
        return
    raise HTTPException(
        status_code=403,
        detail="No tienes permiso para acceder a los recursos de este usuario",
    )


def es_token_valido(fecha_creacion: Optional[datetime]) -> bool:
    """Valida el requisito de caducidad de 24 horas."""
    if not fecha_creacion:
        return False
    if fecha_creacion.tzinfo is None:
        fecha_creacion = fecha_creacion.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - fecha_creacion) <= timedelta(hours=24)


def ensure_gestor_role(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Mantiene compatibilidad con las dependencias antiguas de rol sin bloquear."""
    return user
