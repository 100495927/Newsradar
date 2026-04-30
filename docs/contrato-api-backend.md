# Contrato API Backend NewsRadar

Fecha: 2026-04-29

## 1. Objetivo

Este documento fija el contrato de la API del backend tal y como esta implementada hoy en el codigo dividido por modulos. Tambien deja constancia del estado de reconciliacion respecto a la API de referencia entregada por AG.

Fuentes usadas para este contrato:

- Referencia AG original: `docs/archivos_AG/newsradar_api/app/main.py`
- Referencia comentada AG: `docs/archivos_AG/newsradar_api/app/main_comentado.py`
- Implementacion actual: `backend/app/app.py` y `backend/app/*/routes.py`
- Informe previo de diferencias: `docs/informe-conformidad-contrato-api-2026-04-15.md`
- Commit de reconciliacion revisado: `89faddb` (`add: ahora sigue el contrato`)

## 2. Estado de reconciliacion

Conclusion corta: la reconciliacion se ha hecho en gran medida, pero no de forma literalmente identica al AG original.

Que si ha quedado reconciliado:

- El inventario principal de endpoints del AG esta presente en el backend modular actual.
- El commit `89faddb` corrige justo los puntos que el informe del `2026-04-15` marcaba como rotos en `auth/register` y en los endpoints de `users`.
- Los modelos publicos de usuario actuales vuelven a exponer `id` y `role_ids`, alineandose con el shape del AG.

Diferencias residuales que siguen existiendo:

- El backend actual anade endpoints extra no presentes en el AG:
  - `GET /api/v1/auth/verify/{token}`
  - `POST /api/v1/auth/forgot-password`
  - `POST /api/v1/auth/reset-password`
  - `GET /api/v1/users/{user_id}/alerts/{alert_id}/notification-settings`
  - `PUT /api/v1/users/{user_id}/alerts/{alert_id}/notification-settings`
  - `GET /api/v1/users/{user_id}/notifications`
  - `GET /api/v1/users/{user_id}/notifications/{notification_id}`
  - `PATCH /api/v1/users/{user_id}/notifications/{notification_id}/read`
- En los modelos de usuario actuales `organization` es opcional, mientras que en el AG original era obligatoria.
- `POST /api/v1/auth/register` devuelve `201 Created` en la implementacion actual; en el AG original no fijaba `201` y por defecto quedaba en `200 OK`.
- `POST /api/v1/users/{user_id}/alerts` anade una restriccion funcional adicional: requiere rol `manager`.
- La autenticacion interna ya no usa tokens en memoria como el AG original; usa JWT. El shape externo del token sigue siendo compatible: `{ "access_token": "...", "token_type": "bearer" }`.

Por tanto, a efectos de trabajo de backend y frontend, el contrato util debe considerarse el del backend actual modular, con las diferencias anteriores anotadas como desviaciones o extensiones respecto al AG.

## 3. Convenciones generales

- Prefijo comun: `/api/v1`
- Formato: JSON salvo respuestas `204 No Content`
- Autenticacion: `Authorization: Bearer <token>`
- Healthcheck sin autenticacion: `GET /api/v1/health`
- La mayoria de endpoints requieren autenticacion

Codigos de error observables en el contrato:

- `400 Bad Request`: validaciones de negocio, token caducado, roles inexistentes
- `401 Unauthorized`: token ausente, invalido o credenciales invalidas
- `403 Forbidden`: permiso insuficiente
- `404 Not Found`: recurso no encontrado
- `409 Conflict`: email duplicado o borrado no permitido por dependencia

## 4. Modelos del contrato

### 4.1 Auth

`LoginRequest`

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

`TokenResponse`

```json
{
  "access_token": "jwt-o-token-bearer",
  "token_type": "bearer"
}
```

### 4.2 Roles y usuarios

`Role`

```json
{
  "id": 1,
  "name": "admin"
}
```

`User`

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "Ada",
  "last_name": "Lovelace",
  "organization": "NewsRadar",
  "role_ids": [1, 2]
}
```

`UserCreate`

```json
{
  "email": "user@example.com",
  "first_name": "Ada",
  "last_name": "Lovelace",
  "organization": "NewsRadar",
  "role_ids": [2],
  "password": "secret123"
}
```

`UserUpdate`

```json
{
  "email": "nuevo@example.com",
  "first_name": "Ada",
  "last_name": "Lovelace",
  "organization": "NewsRadar",
  "role_ids": [2],
  "password": "nuevo-secret"
}
```

Nota: en la implementacion actual `organization` puede venir como `null` u omitirse en algunos flujos, aunque el AG original la trataba como obligatoria.

### 4.3 Alertas y notificaciones

Actualizacion contractual aplicada el `2026-04-29`:

- `Alert`, `AlertCreate` y `AlertUpdate` incorporan los campos `rss_channels_ids` e `information_sources_ids`.
- En esta fase el contrato publico ya refleja esos campos, aunque su explotacion funcional interna puede evolucionar despues.
- Aunque `categories` se modela como lista por compatibilidad y futura extension, funcionalmente la alerta debe llevar por ahora una sola categoria IPTC.
- Si la alerta selecciona `rss_channels_ids` o `information_sources_ids`, esos canales o fuentes deben ser compatibles con la categoria de la alerta; en caso contrario la API respondera `400 Bad Request`.

`AlertCategoryItem`

```json
{
  "code": "politics",
  "label": "Politics"
}
```

`Alert`

```json
{
  "id": 1,
  "user_id": 3,
  "name": "Elecciones",
  "descriptors": ["congreso", "senado"],
  "categories": [
    { "code": "politics", "label": "Politics" }
  ],
  "rss_channels_ids": ["rss-elpais-politica", "rss-rtve-nacional"],
  "information_sources_ids": ["elpais", "rtve"],
  "cron_expression": "0 0 * * *"
}
```

`AlertCreate`

```json
{
  "name": "Elecciones",
  "descriptors": ["congreso", "senado"],
  "categories": [
    { "code": "politics", "label": "Politics" }
  ],
  "rss_channels_ids": ["rss-elpais-politica", "rss-rtve-nacional"],
  "information_sources_ids": ["elpais", "rtve"],
  "cron_expression": "0 0 * * *"
}
```

`AlertUpdate`

```json
{
  "name": "Elecciones Europa",
  "descriptors": ["parlamento europeo"],
  "categories": [
    { "code": "politics", "label": "Politics" }
  ],
  "rss_channels_ids": ["rss-euronews-politics"],
  "information_sources_ids": ["euronews"],
  "cron_expression": "*/15 * * * *"
}
```

`Notification`

```json
{
  "id": 1,
  "alert_id": 10,
  "timestamp": "2026-04-18T10:00:00Z",
  "metrics": [
    { "name": "mentions", "value": 14.0 }
  ]
}
```

### 4.4 Categorias, fuentes RSS y estadisticas

`Category`

```json
{
  "id": 1,
  "name": "Politics",
  "source": "IPTC"
}
```

`InformationSource`

```json
{
  "id": 1,
  "name": "El Pais",
  "url": "https://elpais.com"
}
```

`RSSChannel`

```json
{
  "id": 1,
  "information_source_id": 1,
  "url": "https://elpais.com/rss",
  "category_id": 2
}
```

`Metric`

```json
{
  "name": "articles_processed",
  "value": 42.0
}
```

`Stats`

```json
{
  "id": 1,
  "metrics": [
    { "name": "articles_processed", "value": 42.0 }
  ]
}
```

## 5. Endpoints del contrato actual

### 5.1 Sistema

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/health` | No | Sin body | `{ status, timestamp }` | Endpoint de healthcheck |

### 5.2 Auth

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| POST | `/api/v1/auth/login` | No | `LoginRequest` | `TokenResponse` | Devuelve token Bearer |
| POST | `/api/v1/auth/register` | No | `UserCreate` | `User` | En actual responde `201` |
| GET | `/api/v1/auth/verify/{token}` | No | Path param `token` | `{ "message": "Cuenta verificada correctamente" }` | Extension respecto al AG |
| POST | `/api/v1/auth/forgot-password` | No | Modelo actual: `LoginRequest` | `{ "message": "Si el email esta registrado, recibira instrucciones de recuperacion" }` | La implementacion solo usa `email`, pero el schema actual reutiliza `LoginRequest` |
| POST | `/api/v1/auth/reset-password` | No | Query params `token`, `new_password` | `{ "message": "Contrasena actualizada correctamente" }` | Extension respecto al AG |

### 5.3 Usuarios

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/users` | Si | Sin body | `List[User]` | Lista usuarios sin password |
| POST | `/api/v1/users` | Si | `UserCreate` | `User` | `201 Created` |
| GET | `/api/v1/users/{user_id}` | Si | Path param `user_id` | `User` | |
| PUT | `/api/v1/users/{user_id}` | Si | `UserUpdate` | `User` | Solo el propio usuario o admin puede editar |
| DELETE | `/api/v1/users/{user_id}` | Si | Path param `user_id` | Sin body | `204 No Content`; borra alertas y notificaciones en cascada |

### 5.4 Roles

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/roles` | Si | Sin body | `List[Role]` | |
| POST | `/api/v1/roles` | Si | `RoleCreate` | `Role` | `201 Created` |
| GET | `/api/v1/roles/{role_id}` | Si | Path param `role_id` | `Role` | |
| PUT | `/api/v1/roles/{role_id}` | Si | `RoleUpdate` | `Role` | |
| DELETE | `/api/v1/roles/{role_id}` | Si | Path param `role_id` | Sin body | `204 No Content`; puede devolver `409` si el rol esta asignado |

### 5.5 Alertas

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/users/{user_id}/alerts` | Si | Path param `user_id` | `List[Alert]` | |
| POST | `/api/v1/users/{user_id}/alerts` | Si | `AlertCreate` | `Alert` | `201 Created`; requiere rol `manager`; `400` si la alerta no tiene exactamente una categoria valida o si sus fuentes/canales no son compatibles con ella |
| GET | `/api/v1/users/{user_id}/alerts/{alert_id}` | Si | Path params | `Alert` | |
| PUT | `/api/v1/users/{user_id}/alerts/{alert_id}` | Si | `AlertUpdate` | `Alert` | `400` si deja la alerta con categorias/fuentes incompatibles |
| DELETE | `/api/v1/users/{user_id}/alerts/{alert_id}` | Si | Path params | Sin body | `204 No Content`; borra notificaciones asociadas |

### 5.6 Notificaciones

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/users/{user_id}/alerts/{alert_id}/notifications` | Si | Path params | `List[Notification]` | |
| POST | `/api/v1/users/{user_id}/alerts/{alert_id}/notifications` | Si | `NotificationCreate` | `Notification` | `201 Created` |
| GET | `/api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}` | Si | Path params | `Notification` | |
| PUT | `/api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}` | Si | `NotificationUpdate` | `Notification` | |
| DELETE | `/api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}` | Si | Path params | Sin body | `204 No Content` |

### 5.7 Categorias

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/categories` | Si | Sin body | `List[Category]` | |
| POST | `/api/v1/categories` | Si | `CategoryCreate` | `Category` | `201 Created` |
| GET | `/api/v1/categories/{category_id}` | Si | Path param `category_id` | `Category` | |
| PUT | `/api/v1/categories/{category_id}` | Si | `CategoryUpdate` | `Category` | |
| DELETE | `/api/v1/categories/{category_id}` | Si | Path param `category_id` | Sin body | `204 No Content`; puede devolver `409` si la categoria esta en uso |

### 5.8 Fuentes de informacion y canales RSS

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/information-sources` | Si | Sin body | `List[InformationSource]` | |
| POST | `/api/v1/information-sources` | Si | `InformationSourceCreate` | `InformationSource` | `201 Created` |
| GET | `/api/v1/information-sources/{source_id}` | Si | Path param `source_id` | `InformationSource` | |
| PUT | `/api/v1/information-sources/{source_id}` | Si | `InformationSourceUpdate` | `InformationSource` | |
| DELETE | `/api/v1/information-sources/{source_id}` | Si | Path param `source_id` | Sin body | `204 No Content`; borra canales RSS asociados |
| GET | `/api/v1/information-sources/{source_id}/rss-channels` | Si | Path param `source_id` | `List[RSSChannel]` | |
| POST | `/api/v1/information-sources/{source_id}/rss-channels` | Si | `RSSChannelCreate` | `RSSChannel` | `201 Created`; valida `category_id` |
| GET | `/api/v1/information-sources/{source_id}/rss-channels/{channel_id}` | Si | Path params | `RSSChannel` | |
| PUT | `/api/v1/information-sources/{source_id}/rss-channels/{channel_id}` | Si | `RSSChannelUpdate` | `RSSChannel` | |
| DELETE | `/api/v1/information-sources/{source_id}/rss-channels/{channel_id}` | Si | Path params | Sin body | `204 No Content` |

### 5.9 Stats

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/stats` | Si | Sin body | `List[Stats]` | |
| POST | `/api/v1/stats` | Si | `StatsCreate` | `Stats` | `201 Created` |
| GET | `/api/v1/stats/{stats_id}` | Si | Path param `stats_id` | `Stats` | |
| PUT | `/api/v1/stats/{stats_id}` | Si | `StatsUpdate` | `Stats` | |
| DELETE | `/api/v1/stats/{stats_id}` | Si | Path param `stats_id` | Sin body | `204 No Content` |

### 5.10 Extensiones del backend fuera del contrato original

Esta subseccion describe funcionalidades implementadas en el backend actual que no forman parte de la API original entregada por AG.

Regla de interpretacion:

- estas rutas no pertenecen al contrato base
- estas rutas son extensiones especificas del proyecto actual
- frontend, tests y documentacion deben tratarlas como extension y no como parte de la API normal/AG

#### 5.10.1 Configuracion de entrega por alerta

El enunciado si parece pedir esta capacidad y la vincula a la alerta, no al perfil. La frase relevante es:

- "La alerta se podra configurar para que envie notificaciones al buzon de la aplicacion o al correo electronico del usuario"

Por tanto, la interpretacion adoptada es esta:

- la configuracion pertenece a cada alerta
- no se ha encontrado en la API AG original un campo equivalente en `Alert`
- no se ha encontrado en perfil de usuario ni en otros modelos del AG un hueco contractual para expresar esta configuracion
- para no romper el contrato original, esta capacidad se expone como extension

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/users/{user_id}/alerts/{alert_id}/notification-settings` | Si | Path params | `{ "channels": ["app", "email"] }` | Extension fuera del contrato original |
| PUT | `/api/v1/users/{user_id}/alerts/{alert_id}/notification-settings` | Si | `{ "channels": ["app"] }` o similar | `{ "channels": [...] }` | Extension fuera del contrato original |

#### 5.10.2 Buzon global del usuario

Estas rutas exponen la notificacion interna rica persistida en MongoDB.

Tambien son extension porque el modelo publico `Notification` del AG solo incluye:

- `id`
- `alert_id`
- `timestamp`
- `metrics`

| Metodo | Ruta | Auth | Request | Response | Notas |
|---|---|---|---|---|---|
| GET | `/api/v1/users/{user_id}/notifications` | Si | Path param `user_id` | `List[NotificationMailboxItem]` | Extension fuera del contrato original |
| GET | `/api/v1/users/{user_id}/notifications/{notification_id}` | Si | Path params | `NotificationMailboxItem` | Extension fuera del contrato original |
| PATCH | `/api/v1/users/{user_id}/notifications/{notification_id}/read` | Si | Path params | `{ "id": 1, "read_at": "..." }` | Extension fuera del contrato original |

## 6. Observaciones de implementacion que conviene no confundir con el contrato

- El backend actual esta dividido por modulos, pero `auth/routes.py` concentra tambien los endpoints de `users` y `roles`.
- La persistencia actual es:
  - MongoDB para usuarios, fuentes, canales RSS, alertas, notificaciones, stats y counters.
  - Memoria para roles y categorias.
- El contrato externo de la API no depende de esa separacion interna, pero si afecta a semillas, tests y comportamiento de arranque.
- En `backend/app/app.py` el `startup` de semillas si esta activo actualmente.

## 7. Recomendacion de uso

Si el equipo necesita una referencia contractual unica para seguir desarrollando frontend, tests o integraciones, la base debe ser este documento y no el informe del `2026-04-15`, porque ese informe ya no refleja los cambios introducidos despues de la reconciliacion inicial.

Si en algun momento se quiere volver a una conformidad estricta con el AG original, los ajustes pendientes a revisar son:

- Hacer obligatoria `organization` en los modelos publicos y de entrada de usuario.
- Decidir si `POST /auth/register` debe volver a `200 OK` o si se acepta `201 Created` como nueva convencion.
- Decidir si las extensiones de verificacion y reseteo de password pasan a formar parte oficial del contrato compartido.
- Decidir si la restriccion de rol en creacion de alertas debe considerarse regla funcional oficial del producto.
- Decidir si las rutas de configuracion de entrega y buzon global se mantienen como extension permanente o se documentan en una futura v2 del contrato.
