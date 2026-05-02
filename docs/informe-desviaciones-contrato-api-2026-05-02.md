# Informe de desviaciones respecto al contrato de API

Fecha: 2026-05-02

## 1. Objetivo

Este documento recoge los puntos en los que la implementacion actual del backend no sigue de forma literal el contrato de API que el propio repositorio declara en `docs/contrato-api-backend.md`.

No compara solo con la API original de AG, sino con el contrato util vigente que el equipo ha documentado como referencia interna.

Fuentes revisadas:

- Contrato declarado: `docs/contrato-api-backend.md`
- Referencia AG: `docs/archivos_AG/newsradar_api/app/main.py`
- Implementacion actual:
  - `backend/app/app.py`
  - `backend/app/auth/routes.py`
  - `backend/app/alertas/routes.py`
  - `backend/app/category/routes.py`
  - `backend/app/notificaciones/routes.py`
  - `backend/app/rss/routes.py`
  - `backend/app/stats/routes.py`
  - `backend/app/dependencies.py`

## 2. Resumen ejecutivo

La situacion actual es esta:

- En alertas, notificaciones y RSS hay una alineacion estructural razonable con el contrato.
- El contrato si describe correctamente que la version de la API usada ya incluye `categories`, `rss_channels_ids` e `information_sources_ids` en alertas.
- Aun asi, siguen existiendo desviaciones funcionales y contractuales relevantes en `auth/register`, `roles`, `users`, `categories` y parte de `alerts`.
- Ademas, el backend expone endpoints reales de `stats` que no estan reflejados en el contrato actual.

## 3. Desviaciones vigentes

### 3.1 `POST /api/v1/auth/register`

Contrato declarado:

- Ruta: `POST /api/v1/auth/register`
- Request: `UserCreate`
- Response: `User`
- Nota del contrato: en la implementacion actual responde `201`

Implementacion real:

- La ruta devuelve `TokenResponse`, no `User`.
- El backend registra al usuario y hace login automatico devolviendo JWT.

Referencias:

- Contrato: `docs/contrato-api-backend.md`
- Implementacion: `backend/app/auth/routes.py`

Impacto:

- Cualquier cliente que espere un `User` segun el contrato fallara al integrar con la implementacion real.
- La documentacion actual no describe el shape real de la respuesta.

### 3.2 Modelo y semantica de usuarios

Contrato declarado:

- `User` expone `id`, `email`, `first_name`, `last_name`, `organization`, `role_ids`
- `UserCreate` y `UserUpdate` aceptan `role_ids`
- `PUT /users/{user_id}` permite editar al propio usuario o a un admin

Implementacion real:

- El modelo publico sigue exponiendo `role_ids`, pero la semantica real de roles ya no coincide con lo documentado.
- En `register` y `create_user` se ignoran los `role_ids` enviados y se asigna siempre el rol canonico por defecto.
- `ensure_role_ids_exist()` ya no valida nada.
- `ensure_user_can_access()` solo permite acceso al propio usuario y bloquea cualquier edicion transversal; no existe excepcion real de admin.

Referencias:

- Contrato: `docs/contrato-api-backend.md`
- Modelos: `backend/app/auth/user.py`
- Rutas: `backend/app/auth/routes.py`
- Permisos: `backend/app/dependencies.py`

Impacto:

- El contrato sugiere una API multirol real, pero el backend opera de facto con un unico rol funcional.
- El contrato de permisos de `PUT /users/{user_id}` no describe el comportamiento observable real.

### 3.3 CRUD de roles

Contrato declarado:

- CRUD normal de `roles`
- `DELETE /roles/{role_id}` puede devolver `409` si el rol esta asignado

Implementacion real:

- `GET /roles` devuelve siempre un unico rol canonico `manager`.
- `POST /roles` acepta la llamada por compatibilidad, pero no crea roles reales.
- `GET /roles/{role_id}` devuelve una respuesta sintetica incluso para IDs arbitrarios.
- `PUT /roles/{role_id}` no modifica un registro persistente real.
- `DELETE /roles/{role_id}` acepta el borrado por compatibilidad sin comprobar existencia ni dependencias.

Referencias:

- Contrato: `docs/contrato-api-backend.md`
- Implementacion: `backend/app/auth/routes.py`

Impacto:

- El contrato actual presenta `roles` como recurso real cuando en la implementacion solo queda una capa de compatibilidad.
- Los codigos esperables `404` o `409` dejan de ser fiables para clientes que consuman estas rutas.

### 3.4 CRUD de categorias

Contrato declarado:

- CRUD normal de `categories`
- `POST` crea
- `PUT` actualiza
- `DELETE` borra y puede devolver `409` si la categoria esta en uso

Implementacion real:

- `POST /categories` no persiste en el catalogo canonico; responde una categoria resuelta o una categoria ficticia.
- `PUT /categories/{category_id}` no actualiza realmente el catalogo canonico.
- `DELETE /categories/{category_id}` no elimina la categoria; solo comprueba si existen canales RSS activos asociados.
- `DELETE` puede devolver `204` aunque la categoria no exista, siempre que no haya canales asociados.

Referencias:

- Contrato: `docs/contrato-api-backend.md`
- Implementacion: `backend/app/category/routes.py`

Impacto:

- El contrato describe operaciones mutables reales, pero la implementacion ofrece una compatibilidad superficial.
- Esto puede inducir a error en frontend, tests de integracion y clientes externos.

### 3.5 Restriccion de rol en alertas

Contrato declarado:

- `POST /users/{user_id}/alerts` requiere rol `manager`

Implementacion real:

- La ruta depende de `ensure_gestor_role`, pero esa dependencia no restringe nada y devuelve el usuario autenticado sin validar rol.
- En la practica, cualquier usuario autenticado puede pasar esa comprobacion.

Referencias:

- Contrato: `docs/contrato-api-backend.md`
- Implementacion: `backend/app/alertas/routes.py`
- Dependencia: `backend/app/dependencies.py`

Impacto:

- El contrato comunica una restriccion de autorizacion que no existe realmente.

### 3.6 Cardinalidad real de `categories` en alertas

Contrato declarado:

- La alerta debe llevar exactamente una categoria IPTC valida

Implementacion real:

- El backend exige que exista al menos una categoria, pero no rechaza listas con varias.
- Toma la primera categoria y descarta el resto de forma implicita.

Referencias:

- Contrato: `docs/contrato-api-backend.md`
- Implementacion: `backend/app/alertas/routes.py`

Impacto:

- El comportamiento observable no coincide con la restriccion documentada.
- Un cliente puede enviar varias categorias y obtener `201` o `200` cuando el contrato hacia esperar `400`.

### 3.7 Endpoints de `stats` no documentados en el contrato actual

Contrato declarado:

- Solo documenta el CRUD de `/api/v1/stats`

Implementacion real:

- El backend tambien expone:
  - `GET /api/v1/stats/global`
  - `GET /api/v1/stats/timeline`
  - `GET /api/v1/stats/feed/{feed_id}`
  - `GET /api/v1/stats/cloud/{categoria}`

Referencias:

- Contrato: `docs/contrato-api-backend.md`
- Implementacion: `backend/app/stats/routes.py`

Impacto:

- El contrato actual es incompleto respecto a endpoints realmente publicados por el backend.
- Esto no rompe compatibilidad hacia atras, pero si deja fuera parte de la superficie real de la API.

## 4. Puntos que si parecen alineados en esta revision

En esta revision no se han detectado desviaciones estructurales relevantes en estos bloques del contrato:

- Shape publico de `Alert`, `AlertCreate` y `AlertUpdate` con:
  - `categories`
  - `rss_channels_ids`
  - `information_sources_ids`
- Endpoints principales de alertas:
  - `GET /users/{user_id}/alerts`
  - `GET /users/{user_id}/alerts/{alert_id}`
  - `PUT /users/{user_id}/alerts/{alert_id}`
  - `DELETE /users/{user_id}/alerts/{alert_id}`
- Endpoints contractuales de notificaciones por alerta
- Endpoints de `information-sources` y `rss-channels` en su shape publico principal

Nota:

- Que un bloque este alineado en shape no implica que toda su logica de negocio coincida exactamente con el AG original; aqui solo se marca que no se ha encontrado una desviacion contractual mayor frente al contrato actual del repositorio.

## 5. Recomendaciones

Opciones razonables para dejar de tener esta divergencia:

1. Ajustar el documento `docs/contrato-api-backend.md` para que describa el backend real tal como funciona hoy.
2. O bien corregir el backend para volver a cumplir literalmente el contrato documentado en:
   - `auth/register`
   - `roles`
   - `users`
   - `categories`
   - validacion estricta de `categories` en alertas
3. Si se mantiene la capa de compatibilidad actual, dejar explicitamente marcados `roles` y `categories` como endpoints de compatibilidad y no como recursos CRUD reales.

## 6. Alcance de esta revision

Esta revision se ha hecho por inspeccion estatica de codigo y documentacion.

No se han ejecutado en este informe:

- pruebas end-to-end contra la API levantada
- llamadas HTTP reales a cada endpoint
- validaciones OpenAPI generadas desde `/docs`

Por tanto, el informe describe desviaciones observables en codigo, que son suficientes para documentar el problema, pero conviene complementar con una verificacion funcional si se quiere cerrar el tema para entrega o frontend.
