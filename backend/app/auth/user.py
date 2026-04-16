from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -- Roles --

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


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
    organization: Optional[str] = Field(None, max_length=180)


class UserCreate(UserBase):
    role_ids: List[int] = []
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=120)
    last_name: Optional[str] = Field(None, min_length=1, max_length=120)
    organization: Optional[str] = Field(None, max_length=180)
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
