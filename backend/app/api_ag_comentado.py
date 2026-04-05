from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from uuid import uuid4
from pymongo import MongoClient
import os
import hashlib

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, HttpUrl

# API de referencia para el contrato funcional de NewsRadar.
# Nota: esta version usa almacenamiento en memoria (no persistente).
app = FastAPI(
    title="NewsRadar API",
    version="1.0.0",
    description="API REST para gestión de usuarios, alertas, notificaciones, fuentes y canales RSS.",
)

API_PREFIX = "/api/v1"
security = HTTPBearer(auto_error=False)


class Metric(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: float


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class Role(RoleBase):
    id: int


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=120)
    last_name: str = Field(..., min_length=1, max_length=120)
    organization: str = Field(..., min_length=1, max_length=180)
    role_ids: List[int] = Field(default_factory=list)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=120)
    last_name: Optional[str] = Field(None, min_length=1, max_length=120)
    organization: Optional[str] = Field(None, min_length=1, max_length=180)
    role_ids: Optional[List[int]] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)


class User(UserBase):
    id: int


class UserInDB(User):
    password: str
    is_verified: bool = False  # Requisito: verificación de cuenta 
    verification_token: Optional[str] = None
    token_created_at: Optional[datetime] = None # Para controlar las 24 horas


class AlertCategoryItem(BaseModel):
    code: str = Field(..., min_length=1, max_length=60)
    label: str = Field(..., min_length=1, max_length=120)


class AlertBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    descriptors: List[str] = Field(default_factory=list)
    categories: List[AlertCategoryItem] = Field(default_factory=list)
    cron_expression: str = Field(..., min_length=1, max_length=120)


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    descriptors: Optional[List[str]] = None
    categories: Optional[List[AlertCategoryItem]] = None
    cron_expression: Optional[str] = Field(None, min_length=1, max_length=120)


class Alert(AlertBase):
    id: int
    user_id: int


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    source: str = Field(default="IPTC", pattern="^IPTC$")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    source: Optional[str] = Field(None, pattern="^IPTC$")


class Category(CategoryBase):
    id: int


class NotificationBase(BaseModel):
    timestamp: datetime
    metrics: List[Metric] = Field(default_factory=list)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    metrics: Optional[List[Metric]] = None


class Notification(NotificationBase):
    id: int
    alert_id: int


class InformationSourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    url: HttpUrl


class InformationSourceCreate(InformationSourceBase):
    pass


class InformationSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    url: Optional[HttpUrl] = None


class InformationSource(InformationSourceBase):
    id: int


class RSSChannelBase(BaseModel):
    url: HttpUrl
    category_id: int


class RSSChannelCreate(RSSChannelBase):
    pass


class RSSChannelUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    category_id: Optional[int] = None


class RSSChannel(RSSChannelBase):
    id: int
    information_source_id: int


class StatsBase(BaseModel):
    metrics: List[Metric] = Field(default_factory=list)


class StatsCreate(StatsBase):
    pass


class StatsUpdate(BaseModel):
    metrics: Optional[List[Metric]] = None


class Stats(StatsBase):
    id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


roles_store: Dict[int, Role] = {}
users_store: Dict[int, UserInDB] = {}
alerts_store: Dict[int, Alert] = {}
categories_store: Dict[int, Category] = {}
notifications_store: Dict[int, Notification] = {}
information_sources_store: Dict[int, InformationSource] = {}
rss_channels_store: Dict[int, RSSChannel] = {}
stats_store: Dict[int, Stats] = {}

active_tokens: Dict[str, int] = {}

# Conexion a la base de datos
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@mongodb:27017/")
client = MongoClient(MONGO_URI)
db = client["newsradar_db"]
users_col = db["users"] # Esta será tu colección principal de usuarios

counters = {
    "roles": 1,
    "users": 1,
    "alerts": 1,
    "categories": 1,
    "notifications": 1,
    "information_sources": 1,
    "rss_channels": 1,
    "stats": 1,
}


def next_id(counter_key: str) -> int:
    """Genera IDs autoincrementales por tipo de entidad."""
    value = counters[counter_key]
    counters[counter_key] += 1
    return value


def ensure_role_ids_exist(role_ids: List[int]) -> None:
    """Valida que los IDs de rol enviados existan en el store de roles."""
    missing = [role_id for role_id in role_ids if role_id not in roles_store]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles no encontrados: {missing}",
        )


def ensure_user_exists(user_id: int) -> None:
    """Lanza 404 si el usuario no existe."""
    if user_id not in users_store:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


def ensure_alert_for_user(user_id: int, alert_id: int) -> Alert:
    """Comprueba que la alerta exista y pertenezca al usuario indicado."""
    alert = alerts_store.get(alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alerta no encontrada para el usuario")
    return alert


def ensure_notification_for_alert(alert_id: int, notification_id: int) -> Notification:
    """Comprueba que la notificacion exista y pertenezca a la alerta indicada."""
    notification = notifications_store.get(notification_id)
    if not notification or notification.alert_id != alert_id:
        raise HTTPException(status_code=404, detail="Notificación no encontrada para la alerta")
    return notification


def ensure_information_source_exists(source_id: int) -> None:
    """Lanza 404 si la fuente de informacion no existe."""
    if source_id not in information_sources_store:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")


def ensure_category_exists(category_id: int) -> None:
    """Lanza 404 si la categoria no existe."""
    if category_id not in categories_store:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")


def ensure_rss_for_source(source_id: int, channel_id: int) -> RSSChannel:
    """Valida que el canal RSS exista y cuelgue de la fuente indicada."""
    channel = rss_channels_store.get(channel_id)
    if not channel or channel.information_source_id != source_id:
        raise HTTPException(status_code=404, detail="Canal RSS no encontrado para la fuente")
    return channel


def sanitize_user(user: UserInDB) -> User:
    """Devuelve la vista publica del usuario sin password."""
    return User(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=user.organization,
        role_ids=user.role_ids,
    )


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


def es_token_valido(fecha_creacion: Optional[datetime]) -> bool:
    """Valida el requisito de caducidad de 24 horas."""
    if not fecha_creacion:
        return False
    limite = timedelta(hours=24)
    # Comparamos el tiempo actual con el de creación 
    return (datetime.now(timezone.utc) - fecha_creacion) <= limite

def ensure_gestor_role(user: UserInDB = Depends(get_current_user)):
    """Verifica que el usuario no sea solo un 'Lector'."""
    # Buscamos si el usuario tiene el rol de admin/gestor [cite: 45, 81]
    is_gestor = any(roles_store[r_id].name == "admin" for r_id in user.role_ids)
    if not is_gestor:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: Se requiere rol de Gestor de NewsRadar "
        )
    return user



def create_seed_data() -> None:
    """Carga datos semilla (roles y admin) en el arranque si no existen."""
    if roles_store:
        return

    admin_role_id = next_id("roles")
    roles_store[admin_role_id] = Role(id=admin_role_id, name="admin")

    user_role_id = next_id("roles")
    roles_store[user_role_id] = Role(id=user_role_id, name="user")

    admin_user_id = next_id("users")
    users_store[admin_user_id] = UserInDB(
        id=admin_user_id,
        email="admin@newsradar.com",
        first_name="Admin",
        last_name="NewsRadar",
        organization="NewsRadar",
        role_ids=[admin_role_id],
        password="admin123",
    )


@app.on_event("startup")
def on_startup() -> None:
    """Hook de inicio para inicializar datos basicos."""
    create_seed_data()


@app.get(f"{API_PREFIX}/health", tags=["system"])
def health() -> dict:
    """Endpoint de healthcheck para comprobar que la API responde."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post(f"{API_PREFIX}/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: LoginRequest) -> TokenResponse:
    """Autentica por email/password y devuelve token Bearer temporal."""
    user = next((u for u in users_store.values() if u.email == payload.email), None)
    if user is None or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = str(uuid4())
    active_tokens[token] = user.id
    return TokenResponse(access_token=token)


@app.post(f"{API_PREFIX}/auth/register", response_model=User, tags=["auth"])
def register(payload: UserCreate) -> User:
    """Registra un usuario nuevo validando email unico y roles existentes."""
    if any(user.email == payload.email for user in users_store.values()):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    ensure_role_ids_exist(payload.role_ids)

    user_id = next_id("users")
    # Añadimos la lógica de verificación al crear el objeto 
    user_db = UserInDB(
        id=user_id, 
        verification_token=str(uuid4()), 
        token_created_at=datetime.now(timezone.utc),
        **payload.model_dump()
    )
    users_store[user_id] = user_db
    # IMPORTANTE: Aquí deberías imprimir el token en el log para simular el envío de email [cite: 69]
    print(f"DEBUG: Token para {user_db.email}: {user_db.verification_token}")
    return sanitize_user(user_db)


@app.get(f"{API_PREFIX}/auth/verify/{{token}}", tags=["auth"])
def verify_email(token: str):
    """Verifica la cuenta si el token no ha expirado."""
    user = next((u for u in users_store.values() if u.verification_token == token), None)
    
    if not user:
        raise HTTPException(status_code=404, detail="Token no válido")
    
    if not es_token_valido(user.token_created_at):
        raise HTTPException(status_code=400, detail="El enlace ha caducado (máximo 24h) ")
    
    user.is_verified = True
    user.verification_token = None 
    return {"message": "Cuenta verificada correctamente "}

@app.post(f"{API_PREFIX}/auth/forgot-password", tags=["auth"])
def forgot_password(payload: LoginRequest):
    # Buscamos al usuario en la colección de MongoDB que definimos antes
    user = users_col.find_one({"email": payload.email})
    
    if user:
        reset_token = str(uuid4())
        # Guardamos el token y la hora actual (UTC) para la validación de 24h
        users_col.update_one(
            {"email": payload.email},
            {"$set": {
                "reset_token": reset_token, 
                "reset_token_at": datetime.now(timezone.utc)
            }}
        )
        # Importante para el "combate": mostrarlo en logs para que el profesor lo vea
        print(f"DEBUG: Token de recuperación para {payload.email}: {reset_token}")
    
    return {"message": "Si el email está registrado, recibirá instrucciones de recuperación"}


@app.post(f"{API_PREFIX}/auth/reset-password", tags=["auth"])
def reset_password(token: str, new_password: str):
    # Buscamos al usuario que posee ese token de reseteo
    user_data = users_col.find_one({"reset_token": token})
    
    # Validamos existencia y la caducidad de 24 horas (Requisito funcional ID 2)
    if not user_data or not es_token_valido(user_data.get("reset_token_at")):
        raise HTTPException(status_code=400, detail="El enlace es inválido o ha caducado (máximo 24h)")

    # Hasheamos la nueva contraseña (Seguridad obligatoria)
    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
    
    # Actualizamos y limpiamos los tokens de la base de datos
    users_col.update_one(
        {"id": user_data["id"]},
        {
            "$set": {"password": hashed_pw}, 
            "$unset": {"reset_token": "", "reset_token_at": ""}
        }
    )
    return {"message": "Contraseña actualizada correctamente"}


@app.get(f"{API_PREFIX}/users", response_model=List[User], tags=["users"])
def list_users(_: UserInDB = Depends(get_current_user)) -> List[User]:
    """Lista usuarios sin exponer contrasenas."""
    return [sanitize_user(user) for user in users_store.values()]


@app.post(f"{API_PREFIX}/users", response_model=User, status_code=201, tags=["users"])
def create_user(payload: UserCreate, _: UserInDB = Depends(get_current_user)) -> User:
    """Crea usuario administrativo autenticado por token."""
    if any(user.email == payload.email for user in users_store.values()):
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    ensure_role_ids_exist(payload.role_ids)
    user_id = next_id("users")
    user_db = UserInDB(id=user_id, **payload.model_dump())
    users_store[user_id] = user_db
    return sanitize_user(user_db)


@app.get(f"{API_PREFIX}/users/{{user_id}}", response_model=User, tags=["users"])
def get_user(user_id: int, _: UserInDB = Depends(get_current_user)) -> User:
    """Recupera un usuario por ID."""
    user = users_store.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return sanitize_user(user)


@app.put(f"{API_PREFIX}/users/{{user_id}}", response_model=User, tags=["users"])
def update_user(user_id: int, payload: UserUpdate, current_user: UserInDB = Depends(get_current_user)) -> User:
    """Actualiza el perfil en MongoDB con restricciones de seguridad."""
    
    # 1. SEGURIDAD: Solo el propio usuario o un admin puede editar
    is_admin = any(roles_store[r_id].name == "admin" for r_id in current_user.role_ids)
    if current_user.id != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este perfil")

    # 2. BÚSQUEDA: Buscamos en MongoDB en lugar de users_store
    user_data = users_col.find_one({"id": user_id})
    if not user_data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 3. FILTRADO: Preparamos los datos enviados
    data = payload.model_dump(exclude_unset=True)
    
    # PROTECCIÓN: Si no es admin, eliminamos campos sensibles del payload
    if not is_admin:
        data.pop("role_ids", None) # Un usuario no puede subirse el rango solo 
        data.pop("email", None)    # El email suele ser el ID, mejor no cambiarlo aquí 

    # 4. PERSISTENCIA: Actualizamos en la base de datos real
    if data:
        users_col.update_one({"id": user_id}, {"$set": data})

    # 5. RETORNO: Obtenemos el objeto actualizado para devolverlo
    updated_user_data = users_col.find_one({"id": user_id})
    # Convertimos el diccionario de Mongo a nuestro objeto Pydantic
    updated_user_obj = UserInDB(**updated_user_data)
    
    return sanitize_user(updated_user_obj)


@app.delete(
    f"{API_PREFIX}/users/{{user_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["users"],
)
def delete_user(user_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina usuario y borra en cascada alertas y notificaciones asociadas."""
    if user_id not in users_store:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    alert_ids = [alert.id for alert in alerts_store.values() if alert.user_id == user_id]
    for alert_id in alert_ids:
        notification_ids = [n.id for n in notifications_store.values() if n.alert_id == alert_id]
        for notification_id in notification_ids:
            notifications_store.pop(notification_id, None)
        alerts_store.pop(alert_id, None)

    users_store.pop(user_id, None)


@app.get(f"{API_PREFIX}/roles", response_model=List[Role], tags=["roles"])
def list_roles(_: UserInDB = Depends(get_current_user)) -> List[Role]:
    """Lista todos los roles."""
    return list(roles_store.values())


@app.post(f"{API_PREFIX}/roles", response_model=Role, status_code=201, tags=["roles"])
def create_role(payload: RoleCreate, _: UserInDB = Depends(get_current_user)) -> Role:
    """Crea un rol nuevo."""
    role_id = next_id("roles")
    role = Role(id=role_id, **payload.model_dump())
    roles_store[role_id] = role
    return role


@app.get(f"{API_PREFIX}/roles/{{role_id}}", response_model=Role, tags=["roles"])
def get_role(role_id: int, _: UserInDB = Depends(get_current_user)) -> Role:
    """Obtiene rol por ID."""
    role = roles_store.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


@app.put(f"{API_PREFIX}/roles/{{role_id}}", response_model=Role, tags=["roles"])
def update_role(role_id: int, payload: RoleUpdate, _: UserInDB = Depends(get_current_user)) -> Role:
    """Actualiza los campos de un rol existente."""
    role = roles_store.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    updated = role.model_copy(update=payload.model_dump(exclude_unset=True))
    roles_store[role_id] = updated
    return updated


@app.delete(
    f"{API_PREFIX}/roles/{{role_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["roles"],
)
def delete_role(role_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina rol si no esta asignado a ningun usuario."""
    if role_id not in roles_store:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    for user in users_store.values():
        if role_id in user.role_ids:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar un rol asignado a usuarios",
            )

    roles_store.pop(role_id, None)


@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts",
    response_model=List[Alert],
    tags=["alerts"],
)
def list_user_alerts(user_id: int, _: UserInDB = Depends(get_current_user)) -> List[Alert]:
    """Lista alertas de un usuario concreto."""
    ensure_user_exists(user_id)
    return [alert for alert in alerts_store.values() if alert.user_id == user_id]


@app.post(
    f"{API_PREFIX}/users/{{user_id}}/alerts",
    response_model=Alert,
    status_code=201,
    tags=["alerts"],
    dependencies=[Depends(ensure_gestor_role)]
)
def create_user_alert(user_id: int, payload: AlertCreate, _: UserInDB = Depends(get_current_user)) -> Alert:
    """Crea una alerta para un usuario."""
    ensure_user_exists(user_id)
    alert_id = next_id("alerts")
    alert = Alert(id=alert_id, user_id=user_id, **payload.model_dump())
    alerts_store[alert_id] = alert
    return alert


@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}",
    response_model=Alert,
    tags=["alerts"],
)
def get_user_alert(user_id: int, alert_id: int, _: UserInDB = Depends(get_current_user)) -> Alert:
    """Recupera una alerta concreta de un usuario."""
    return ensure_alert_for_user(user_id, alert_id)


@app.put(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}",
    response_model=Alert,
    tags=["alerts"],
)
def update_user_alert(
    user_id: int,
    alert_id: int,
    payload: AlertUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Alert:
    """Actualiza una alerta de usuario."""
    alert = ensure_alert_for_user(user_id, alert_id)
    updated = alert.model_copy(update=payload.model_dump(exclude_unset=True))
    alerts_store[alert_id] = updated
    return updated


@app.delete(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["alerts"],
)
def delete_user_alert(user_id: int, alert_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina una alerta y sus notificaciones vinculadas."""
    ensure_alert_for_user(user_id, alert_id)
    notification_ids = [n.id for n in notifications_store.values() if n.alert_id == alert_id]
    for notification_id in notification_ids:
        notifications_store.pop(notification_id, None)
    alerts_store.pop(alert_id, None)


@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications",
    response_model=List[Notification],
    tags=["notifications"],
)
def list_alert_notifications(
    user_id: int,
    alert_id: int,
    _: UserInDB = Depends(get_current_user),
) -> List[Notification]:
    """Lista notificaciones de una alerta."""
    ensure_alert_for_user(user_id, alert_id)
    return [item for item in notifications_store.values() if item.alert_id == alert_id]


@app.post(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications",
    response_model=Notification,
    status_code=201,
    tags=["notifications"],
)
def create_alert_notification(
    user_id: int,
    alert_id: int,
    payload: NotificationCreate,
    _: UserInDB = Depends(get_current_user),
) -> Notification:
    """Crea una notificacion dentro de una alerta."""
    ensure_alert_for_user(user_id, alert_id)
    notification_id = next_id("notifications")
    notification = Notification(id=notification_id, alert_id=alert_id, **payload.model_dump())
    notifications_store[notification_id] = notification
    return notification


@app.get(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    response_model=Notification,
    tags=["notifications"],
)
def get_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    _: UserInDB = Depends(get_current_user),
) -> Notification:
    """Obtiene una notificacion de una alerta concreta."""
    ensure_alert_for_user(user_id, alert_id)
    return ensure_notification_for_alert(alert_id, notification_id)


@app.put(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    response_model=Notification,
    tags=["notifications"],
)
def update_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    payload: NotificationUpdate,
    _: UserInDB = Depends(get_current_user),
) -> Notification:
    """Actualiza una notificacion existente."""
    ensure_alert_for_user(user_id, alert_id)
    notification = ensure_notification_for_alert(alert_id, notification_id)
    updated = notification.model_copy(update=payload.model_dump(exclude_unset=True))
    notifications_store[notification_id] = updated
    return updated


@app.delete(
    f"{API_PREFIX}/users/{{user_id}}/alerts/{{alert_id}}/notifications/{{notification_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["notifications"],
)
def delete_alert_notification(
    user_id: int,
    alert_id: int,
    notification_id: int,
    _: UserInDB = Depends(get_current_user),
) -> None:
    """Elimina una notificacion de una alerta."""
    ensure_alert_for_user(user_id, alert_id)
    ensure_notification_for_alert(alert_id, notification_id)
    notifications_store.pop(notification_id, None)


@app.get(f"{API_PREFIX}/categories", response_model=List[Category], tags=["categories"])
def list_categories(_: UserInDB = Depends(get_current_user)) -> List[Category]:
    """Lista categorias disponibles."""
    return list(categories_store.values())


@app.post(f"{API_PREFIX}/categories", response_model=Category, status_code=201, tags=["categories"])
def create_category(payload: CategoryCreate, _: UserInDB = Depends(get_current_user)) -> Category:
    """Crea una categoria (fuente IPTC en este prototipo)."""
    category_id = next_id("categories")
    category = Category(id=category_id, **payload.model_dump())
    categories_store[category_id] = category
    return category


@app.get(f"{API_PREFIX}/categories/{{category_id}}", response_model=Category, tags=["categories"])
def get_category(category_id: int, _: UserInDB = Depends(get_current_user)) -> Category:
    """Obtiene una categoria por ID."""
    category = categories_store.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@app.put(f"{API_PREFIX}/categories/{{category_id}}", response_model=Category, tags=["categories"])
def update_category(category_id: int, payload: CategoryUpdate, _: UserInDB = Depends(get_current_user)) -> Category:
    """Actualiza una categoria existente."""
    category = categories_store.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    updated = category.model_copy(update=payload.model_dump(exclude_unset=True))
    categories_store[category_id] = updated
    return updated


@app.delete(
    f"{API_PREFIX}/categories/{{category_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["categories"],
)
def delete_category(category_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina categoria solo si no esta asociada a canales RSS."""
    if category_id not in categories_store:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    for channel in rss_channels_store.values():
        if channel.category_id == category_id:
            raise HTTPException(status_code=409, detail="Categoría asociada a canales RSS")

    categories_store.pop(category_id, None)


@app.get(
    f"{API_PREFIX}/information-sources",
    response_model=List[InformationSource],
    tags=["information-sources"],
)
def list_information_sources(_: UserInDB = Depends(get_current_user)) -> List[InformationSource]:
    """Lista fuentes de informacion registradas."""
    return list(information_sources_store.values())


@app.post(
    f"{API_PREFIX}/information-sources",
    response_model=InformationSource,
    status_code=201,
    tags=["information-sources"],
)
def create_information_source(
    payload: InformationSourceCreate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    """Crea una fuente de informacion."""
    source_id = next_id("information_sources")
    source = InformationSource(id=source_id, **payload.model_dump())
    information_sources_store[source_id] = source
    return source


@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    response_model=InformationSource,
    tags=["information-sources"],
)
def get_information_source(source_id: int, _: UserInDB = Depends(get_current_user)) -> InformationSource:
    """Obtiene una fuente de informacion por ID."""
    source = information_sources_store.get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    return source


@app.put(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    response_model=InformationSource,
    tags=["information-sources"],
)
def update_information_source(
    source_id: int,
    payload: InformationSourceUpdate,
    _: UserInDB = Depends(get_current_user),
) -> InformationSource:
    """Actualiza una fuente de informacion."""
    source = information_sources_store.get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")
    updated = source.model_copy(update=payload.model_dump(exclude_unset=True))
    information_sources_store[source_id] = updated
    return updated


@app.delete(
    f"{API_PREFIX}/information-sources/{{source_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["information-sources"],
)
def delete_information_source(source_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina una fuente y borra en cascada sus canales RSS."""
    if source_id not in information_sources_store:
        raise HTTPException(status_code=404, detail="Fuente de información no encontrada")

    channel_ids = [
        channel.id
        for channel in rss_channels_store.values()
        if channel.information_source_id == source_id
    ]
    for channel_id in channel_ids:
        rss_channels_store.pop(channel_id, None)

    information_sources_store.pop(source_id, None)


@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels",
    response_model=List[RSSChannel],
    tags=["rss-channels"],
)
def list_source_channels(source_id: int, _: UserInDB = Depends(get_current_user)) -> List[RSSChannel]:
    """Lista canales RSS asociados a una fuente."""
    ensure_information_source_exists(source_id)
    return [
        channel
        for channel in rss_channels_store.values()
        if channel.information_source_id == source_id
    ]


@app.post(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels",
    response_model=RSSChannel,
    status_code=201,
    tags=["rss-channels"],
)
def create_source_channel(
    source_id: int,
    payload: RSSChannelCreate,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    """Crea un canal RSS para una fuente validando la categoria."""
    ensure_information_source_exists(source_id)
    ensure_category_exists(payload.category_id)

    channel_id = next_id("rss_channels")
    channel = RSSChannel(
        id=channel_id,
        information_source_id=source_id,
        **payload.model_dump(),
    )
    rss_channels_store[channel_id] = channel
    return channel


@app.get(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}",
    response_model=RSSChannel,
    tags=["rss-channels"],
)
def get_source_channel(
    source_id: int,
    channel_id: int,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    """Recupera un canal RSS concreto de una fuente."""
    ensure_information_source_exists(source_id)
    return ensure_rss_for_source(source_id, channel_id)


@app.put(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}",
    response_model=RSSChannel,
    tags=["rss-channels"],
)
def update_source_channel(
    source_id: int,
    channel_id: int,
    payload: RSSChannelUpdate,
    _: UserInDB = Depends(get_current_user),
) -> RSSChannel:
    """Actualiza un canal RSS y valida categoria si cambia."""
    ensure_information_source_exists(source_id)
    channel = ensure_rss_for_source(source_id, channel_id)

    update_data = payload.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        ensure_category_exists(update_data["category_id"])

    updated = channel.model_copy(update=update_data)
    rss_channels_store[channel_id] = updated
    return updated


@app.delete(
    f"{API_PREFIX}/information-sources/{{source_id}}/rss-channels/{{channel_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["rss-channels"],
)
def delete_source_channel(
    source_id: int,
    channel_id: int,
    _: UserInDB = Depends(get_current_user),
) -> None:
    """Elimina un canal RSS de una fuente."""
    ensure_information_source_exists(source_id)
    ensure_rss_for_source(source_id, channel_id)
    rss_channels_store.pop(channel_id, None)


@app.get(f"{API_PREFIX}/stats", response_model=List[Stats], tags=["stats"])
def list_stats(_: UserInDB = Depends(get_current_user)) -> List[Stats]:
    """Lista registros de estadisticas."""
    return list(stats_store.values())


@app.post(f"{API_PREFIX}/stats", response_model=Stats, status_code=201, tags=["stats"])
def create_stats(payload: StatsCreate, _: UserInDB = Depends(get_current_user)) -> Stats:
    """Crea un registro de estadisticas."""
    stats_id = next_id("stats")
    stats = Stats(id=stats_id, **payload.model_dump())
    stats_store[stats_id] = stats
    return stats


@app.get(f"{API_PREFIX}/stats/{{stats_id}}", response_model=Stats, tags=["stats"])
def get_stats(stats_id: int, _: UserInDB = Depends(get_current_user)) -> Stats:
    """Obtiene un registro de estadisticas por ID."""
    stats = stats_store.get(stats_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    return stats


@app.put(f"{API_PREFIX}/stats/{{stats_id}}", response_model=Stats, tags=["stats"])
def update_stats(stats_id: int, payload: StatsUpdate, _: UserInDB = Depends(get_current_user)) -> Stats:
    """Actualiza un registro de estadisticas."""
    stats = stats_store.get(stats_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats no encontrados")

    updated = stats.model_copy(update=payload.model_dump(exclude_unset=True))
    stats_store[stats_id] = updated
    return updated


@app.delete(
    f"{API_PREFIX}/stats/{{stats_id}}",
    status_code=204,
    response_model=None,
    response_class=Response,
    tags=["stats"],
)
def delete_stats(stats_id: int, _: UserInDB = Depends(get_current_user)) -> None:
    """Elimina un registro de estadisticas."""
    if stats_id not in stats_store:
        raise HTTPException(status_code=404, detail="Stats no encontrados")
    stats_store.pop(stats_id, None)
