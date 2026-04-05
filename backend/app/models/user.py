from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

# Definimos los roles permitidos
class UserRole(str, Enum):
    GESTOR = "gestor"
    LECTOR = "lector"

class UserBase(BaseModel):
    # Datos obligatorios
    email: EmailStr
    nombre: str
    apellidos: str
    organizacion: str
    role: UserRole = UserRole.LECTOR  # Por defecto es lector 

class UserCreate(UserBase):
    # Esto es lo que pediremos en el registro
    password: str

class UserInDB(UserBase):
    # Cómo se guarda en MongoDB
    hashed_password: str
    is_verified: bool = False  # Para la verificación por email 
    verification_token: Optional[str] = None
    token_created_at: Optional[datetime] = None  # Para controlar las 24h 

class UserResponse(UserBase):
    # Lo que el Frontend recibirá
    is_verified: bool
    class Config:
        from_attributes = True