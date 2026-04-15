from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth.user import User, UserInDB
from .store import active_tokens, roles_store, users_store

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInDB:
    """Resuelve el usuario autenticado desde un token Bearer en memoria."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Token inválido o ausente")

    user_id = active_tokens.get(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = users_store.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario inválido")

    return user


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


def es_token_valido(fecha_creacion: Optional[datetime]) -> bool:
    """Valida el requisito de caducidad de 24 horas."""
    if not fecha_creacion:
        return False
    return (datetime.now(timezone.utc) - fecha_creacion) <= timedelta(hours=24)


def ensure_gestor_role(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Verifica que el usuario tenga rol de admin/gestor."""
    is_gestor = any(
        roles_store[r_id].name == "admin"
        for r_id in user.role_ids
        if r_id in roles_store
    )
    if not is_gestor:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: Se requiere rol de Gestor de NewsRadar",
        )
    return user
