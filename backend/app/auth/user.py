from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# -- Roles --

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class Role(RoleBase):
    id: int


# -- Users --

class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=120)
    last_name: str = Field(..., min_length=1, max_length=120)
    organization: str = Field(..., min_length=1, max_length=180)
    telfNum: Optional[str] = None


class UserCreate(UserBase):
    role_ids: List[int] = []
    password: str = Field(..., min_length=6, max_length=128)
    telfNum: str = Field(..., min_length=9, max_length=9)

    @field_validator("telfNum")
    def _validate_telfnum(cls, v: str) -> str:  # pragma: no cover - simple validation
        if not isinstance(v, str):
            raise ValueError("telfNum debe ser una cadena de 9 dígitos")
        val = v.strip()
        if len(val) != 9 or not val.isdigit():
            raise ValueError("telfNum debe contener exactamente 9 dígitos")
        return val


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=120)
    last_name: Optional[str] = Field(None, min_length=1, max_length=120)
    organization: Optional[str] = Field(None, min_length=1, max_length=180)
    role_ids: Optional[List[int]] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)


class User(UserBase):
    """Vista pública sin contraseña."""
    id: int
    role_ids: List[int] = []


class UserInDB(UserBase):
    """Documento tal como se almacena en MongoDB."""
    model_config = ConfigDict(extra="ignore")

    id: int = 0
    role_ids: List[int] = []
    role: Optional[str] = None
    status: Optional[str] = None
    password_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Campos auxiliares internos (no en el schema de Mongo pero permitidos)
    verification_token: Optional[str] = None
    token_created_at: Optional[datetime] = None


# -- Auth --

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
