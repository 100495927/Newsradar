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

    doc = {k: v for k, v in doc.items() if k != "_id"}
    return UserInDB(**doc)


def sanitize_user(user: UserInDB) -> User:
    """Devuelve la vista pública del usuario sin password."""
    return User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=user.organization,
        role=user.role,
        status=user.status,
    )


def es_token_valido(fecha_creacion: Optional[datetime]) -> bool:
    """Valida el requisito de caducidad de 24 horas."""
    if not fecha_creacion:
        return False
    return (datetime.now(timezone.utc) - fecha_creacion) <= timedelta(hours=24)


def ensure_gestor_role(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Verifica que el usuario tenga rol de admin o manager."""
    if user.role not in ("admin", "manager"):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: Se requiere rol de Gestor de NewsRadar",
        )
    return user
