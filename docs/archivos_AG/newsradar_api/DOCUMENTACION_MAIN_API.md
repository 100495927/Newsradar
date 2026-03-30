# Documentacion tecnica de main.py (NewsRadar API)

## 1. Resumen

El archivo [newsradar_api/newsradar_api/app/main.py](newsradar_api/newsradar_api/app/main.py) implementa una API REST completa con FastAPI, versionada con el prefijo `/api/v1`.

Caracteristicas principales:

- Modelos de entrada y salida con Pydantic.
- Validacion de datos (emails, URLs, longitudes, patrones).
- Autenticacion por Bearer token simple.
- CRUD de multiples entidades de dominio.
- Almacenamiento en memoria (diccionarios Python), sin persistencia real.

## 2. Arquitectura interna

### 2.1 Configuracion de app

- App FastAPI declarada con metadata OpenAPI: [newsradar_api/newsradar_api/app/main.py](newsradar_api/newsradar_api/app/main.py#L11)
- Prefijo de version: [newsradar_api/newsradar_api/app/main.py](newsradar_api/newsradar_api/app/main.py#L17)
- Seguridad HTTP Bearer: [newsradar_api/newsradar_api/app/main.py](newsradar_api/newsradar_api/app/main.py#L18)

### 2.2 Modelos Pydantic

Se definen modelos para:

- Roles
- Usuarios
- Alertas
- Categorias
- Notificaciones
- Fuentes de informacion
- Canales RSS
- Stats
- Login/Token

Patrones utilizados:

- `Base`, `Create`, `Update`, `Response` por entidad.
- Validaciones con `Field`, `EmailStr`, `HttpUrl`.
- Separacion de `User` y `UserInDB` para evitar exponer password.

### 2.3 Almacenamiento y estado

El estado de la API se mantiene en memoria con diccionarios globales:

- `roles_store`, `users_store`, `alerts_store`, etc.
- `active_tokens` para tokens de sesion.
- `counters` para IDs autoincrementales.

Implicacion: tras reiniciar el servidor, se pierden los datos (excepto semillas recreadas en startup).

## 3. Funciones auxiliares importantes

- `next_id`: genera IDs incrementales por entidad.
- `ensure_role_ids_exist`: valida relaciones de rol.
- `ensure_user_exists`: valida existencia de usuario.
- `ensure_alert_for_user`: valida relacion usuario-alerta.
- `ensure_notification_for_alert`: valida relacion alerta-notificacion.
- `ensure_information_source_exists`: valida fuente.
- `ensure_category_exists`: valida categoria.
- `ensure_rss_for_source`: valida relacion fuente-canal RSS.
- `sanitize_user`: elimina password en respuestas.
- `get_current_user`: autentica por Bearer token.
- `create_seed_data`: crea roles y admin inicial.

## 4. Seguridad y autenticacion

- Login: `POST /api/v1/auth/login`.
- Registro: `POST /api/v1/auth/register`.
- Proteccion de endpoints mediante dependencia `Depends(get_current_user)`.
- Tokens en memoria y sin expiracion real.

Limitaciones actuales:

- No hay JWT firmado.
- No hay refresh tokens.
- No hay revocacion persistente.
- Passwords sin hashing (solo demo).

## 5. Endpoints disponibles

### 5.1 Sistema

- `GET /api/v1/health`

### 5.2 Auth

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`

### 5.3 Usuarios

- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PUT /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`

### 5.4 Roles

- `GET /api/v1/roles`
- `POST /api/v1/roles`
- `GET /api/v1/roles/{role_id}`
- `PUT /api/v1/roles/{role_id}`
- `DELETE /api/v1/roles/{role_id}`

### 5.5 Alertas de usuario

- `GET /api/v1/users/{user_id}/alerts`
- `POST /api/v1/users/{user_id}/alerts`
- `GET /api/v1/users/{user_id}/alerts/{alert_id}`
- `PUT /api/v1/users/{user_id}/alerts/{alert_id}`
- `DELETE /api/v1/users/{user_id}/alerts/{alert_id}`

### 5.6 Notificaciones de alerta

- `GET /api/v1/users/{user_id}/alerts/{alert_id}/notifications`
- `POST /api/v1/users/{user_id}/alerts/{alert_id}/notifications`
- `GET /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}`
- `PUT /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}`
- `DELETE /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}`

### 5.7 Categorias

- `GET /api/v1/categories`
- `POST /api/v1/categories`
- `GET /api/v1/categories/{category_id}`
- `PUT /api/v1/categories/{category_id}`
- `DELETE /api/v1/categories/{category_id}`

### 5.8 Fuentes de informacion

- `GET /api/v1/information-sources`
- `POST /api/v1/information-sources`
- `GET /api/v1/information-sources/{source_id}`
- `PUT /api/v1/information-sources/{source_id}`
- `DELETE /api/v1/information-sources/{source_id}`

### 5.9 Canales RSS por fuente

- `GET /api/v1/information-sources/{source_id}/rss-channels`
- `POST /api/v1/information-sources/{source_id}/rss-channels`
- `GET /api/v1/information-sources/{source_id}/rss-channels/{channel_id}`
- `PUT /api/v1/information-sources/{source_id}/rss-channels/{channel_id}`
- `DELETE /api/v1/information-sources/{source_id}/rss-channels/{channel_id}`

### 5.10 Stats

- `GET /api/v1/stats`
- `POST /api/v1/stats`
- `GET /api/v1/stats/{stats_id}`
- `PUT /api/v1/stats/{stats_id}`
- `DELETE /api/v1/stats/{stats_id}`

## 6. Reglas de integridad implementadas

- No se puede crear usuario con email duplicado.
- No se puede eliminar un rol asignado a usuarios.
- No se puede eliminar categoria si esta asociada a canales RSS.
- Borrados en cascada:
  - Al borrar usuario, borra sus alertas y notificaciones relacionadas.
  - Al borrar fuente, borra sus canales RSS.

## 7. Explicacion de README de la API

Archivo: [newsradar_api/newsradar_api/README.md](newsradar_api/newsradar_api/README.md)

Que comunica correctamente:

- Que es una API REST FastAPI versionada en `/api/v1`.
- Como arrancarla con `uvicorn app.main:app --reload`.
- Dondde ver Swagger/OpenAPI.
- Flujo jerarquico de recursos.
- Entidades con CRUD.

Puntos a revisar:

- Instruccion de activar venv esta en formato Linux/macOS (`source .venv/bin/activate`).
- En Windows deberia ser: `.venv\\Scripts\\Activate.ps1`.
- Numeracion de autenticacion duplicada (aparece otro punto `1.`).
- Hay inconsistencia en usuario semilla (`admin@newsradar.com` vs `admin@newsradar.ai`).
- Conviene aclarar explicitamente que la persistencia es en memoria.

## 8. Estado de desarrollo

El main actual es util como contrato funcional de API para validacion y pruebas manuales, pero no es backend productivo por:

- Falta de persistencia real (MongoDB).
- Falta de seguridad robusta (hashing/JWT real).
- Falta de separacion por capas (routers/services/repositories).
- Todo concentrado en un unico archivo.

Aun asi, es una base muy valida para guiar la implementacion final del backend estandarizado.
