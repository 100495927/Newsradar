# Informe tecnico - Alertas y notificaciones en API/MongoDB

Fecha: 2026-04-19

## 1. Objetivo

Este informe documenta el estado en el que queda la parte de alertas y
notificaciones tras la migracion inicial desde almacenamiento en memoria hacia
MongoDB, manteniendo la maxima prudencia posible respecto al contrato publico
de la API entregada.

La decision principal ha sido separar dos niveles:

- Contrato publico API: mantiene el shape original de `Alert` y `Notification`.
- Persistencia interna MongoDB: guarda campos adicionales necesarios para el
  futuro procesamiento real de alertas, notificaciones, buzon y correo.

Esta separacion responde a la aclaracion recogida en `Dudas NEWSRADAR
20260415.csv`: se puede modificar la implementacion conectandola con los
servicios de negocio, pero se debe respetar la entrada/salida que especifica el
API en terminos de objetos.

## 2. Estado actual

### 2.1 Alertas

Las rutas existentes de alertas siguen siendo las mismas:

- `GET /api/v1/users/{user_id}/alerts`
- `POST /api/v1/users/{user_id}/alerts`
- `GET /api/v1/users/{user_id}/alerts/{alert_id}`
- `PUT /api/v1/users/{user_id}/alerts/{alert_id}`
- `DELETE /api/v1/users/{user_id}/alerts/{alert_id}`

El modelo publico que expone la API conserva los campos del contrato original:

```json
{
  "id": 1,
  "user_id": 3,
  "name": "Elecciones",
  "descriptors": ["congreso", "senado"],
  "categories": [
    { "code": "politics", "label": "Politics" }
  ],
  "cron_expression": "0 0 * * *"
}
```

Internamente, las alertas ya no se guardan en `alerts_store`, sino en la
coleccion MongoDB `alerts`.

Campos internos guardados en MongoDB:

- `category_id`: categoria numerica asociada a la alerta.
- `rss_channel_ids`: canales RSS concretos seleccionados; lista vacia significa
  que el futuro worker podra interpretar "todos los de la categoria".
- `notification_channels`: canales de entrega previstos, por defecto `app` y
  `email`.
- `enabled`: permite activar/desactivar una alerta sin borrarla.
- `last_checked_at`, `last_run_at`, `next_run_at`: marcas preparadas para el
  futuro worker de alertas.
- `created_at`, `updated_at`: auditoria minima.

Reglas actuales implementadas:

- Crear una alerta requiere autenticacion y rol gestor/admin.
- Se acepta `role` de MongoDB (`admin` o `manager`) ademas del antiguo
  `roles_store`/`role_ids`.
- Se limita a 20 alertas por `user_id`, alineado con el requisito de maximo de
  20 alertas por gestor.
- Se rechaza crear o actualizar una alerta dejando `descriptors` vacio, porque
  el enunciado define las alertas sobre una palabra clave/descriptor.

### 2.2 Notificaciones

Las rutas existentes de notificaciones siguen siendo las mismas:

- `GET /api/v1/users/{user_id}/alerts/{alert_id}/notifications`
- `POST /api/v1/users/{user_id}/alerts/{alert_id}/notifications`
- `GET /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}`
- `PUT /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}`
- `DELETE /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}`

El modelo publico que expone la API conserva el shape original:

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

Internamente, las notificaciones ya no se guardan en `notifications_store`, sino
en la coleccion MongoDB `notifications`.

Campos internos guardados en MongoDB:

- `user_id`: usuario destinatario/propietario de la notificacion.
- `subject`: asunto previsto para buzon/correo.
- `matches`: lista futura de noticias RSS coincidentes.
- `delivery_channels`: canales usados o previstos.
- `email_status`: `pending`, `sent`, `failed` o `skipped`.
- `email_sent_at`, `email_error`: trazabilidad de envio.
- `read_at`: marca de lectura para el buzon interno.
- `created_at`, `updated_at`: auditoria minima.

Por prudencia contractual, estos campos internos no se exponen en las respuestas
actuales.

### 2.3 Contadores

Se ha creado la coleccion MongoDB `counters` para IDs enteros compartidos entre
API y futuros workers.

Contadores iniciales:

- `alerts`
- `notifications`

La API usa `next_mongo_id(...)` para generar IDs persistentes en MongoDB, en vez
del contador en memoria.

## 3. Cambios realizados

### 3.1 MongoDB bootstrap

Archivos modificados:

- `scripts/mongo/init-mongo.js`
- `shared/mongo/bootstrap_spec.py`
- `shared/mongo/__init__.py`
- `scripts/mongo/admin/apply_bootstrap.py`

Cambios:

- Nueva coleccion `alerts`.
- Nueva coleccion `notifications`.
- Nueva coleccion `counters`.
- Indices para consultas frecuentes:
  - alertas por `id`.
  - alertas por usuario/estado/proxima ejecucion.
  - alertas por categoria.
  - notificaciones por `id`.
  - notificaciones por alerta y fecha.
  - notificaciones por usuario, lectura y fecha.
  - notificaciones por estado de email.
- Semillas de contadores para `alerts` y `notifications`.

Nota operativa:

- En bases nuevas, `init-mongo.js` crea todo al arrancar MongoDB con volumen
  vacio.
- En bases ya inicializadas, se debe aplicar `scripts/mongo/admin/apply_bootstrap.py`
  con las variables de entorno de Mongo configuradas.

### 3.2 Backend API

Archivos modificados:

- `backend/app/store.py`
- `backend/app/alertas/routes.py`
- `backend/app/notificaciones/routes.py`
- `backend/app/auth/routes.py`
- `backend/app/auth/user.py`
- `backend/app/dependencies.py`

Cambios:

- `store.py` expone `alerts_col`, `notifications_col`, `counters_col` y
  `next_mongo_id`.
- Las rutas de alertas leen/escriben en MongoDB.
- Las rutas de notificaciones leen/escriben en MongoDB.
- El borrado de usuario borra tambien alertas y notificaciones persistidas.
- `UserInDB` acepta `role` y `status` de MongoDB.
- `ensure_gestor_role` permite `role == "admin"` o `role == "manager"` ademas
  de la logica previa con `role_ids`.

## 4. Compatibilidad con el contrato API

### 4.1 Conservado

Se han conservado:

- Las URIs.
- Los metodos HTTP.
- Los modelos publicos `Alert`, `AlertCreate`, `AlertUpdate`.
- Los modelos publicos `Notification`, `NotificationCreate`,
  `NotificationUpdate`.

OpenAPI vuelve a mostrar solo los campos contractuales en alertas y
notificaciones.

### 4.2 Cambio funcional consciente

Hay una restriccion adicional:

- No se permite crear o actualizar una alerta dejandola sin `descriptors`.

Motivo:

- El enunciado define la alerta sobre una palabra clave/descriptor.
- Una alerta sin descriptor no puede ser monitorizada por el futuro worker.

Si se quisiera una compatibilidad estricta con la API original, esta validacion
podria relajarse, pero no es recomendable funcionalmente.

## 5. Encaje con el enunciado y CSV

La implementacion queda alineada con los puntos relevantes:

- Alertas definidas sobre palabra clave/descriptores.
- Maximo de 20 alertas por gestor.
- Posibilidad interna de seleccionar canales RSS concretos.
- Categoria asociada a la alerta.
- Cron expression persistida.
- Preparacion para buzon interno.
- Preparacion para correo electronico.
- Estado de envio de correo externalizable y trazable.
- Credenciales SMTP no se guardan en codigo; deben venir de variables de
  entorno.
- Los lectores no gestionan alertas; la restriccion queda en la dependencia de
  rol gestor/admin.

## 6. Pendiente de implementar

### 6.1 API

Pendientes recomendados:

- Validar `category_id` contra categorias reales cuando se decida exponerlo.
- Validar `rss_channel_ids` contra canales reales cuando se decida exponerlos.
- Decidir si se mantiene solo el endpoint anidado actual o se anade un endpoint
  de buzon global:
  - `GET /api/v1/users/{user_id}/notifications`
  - `PATCH /api/v1/users/{user_id}/notifications/{notification_id}/read`
- Documentar oficialmente si los campos internos se expondran en endpoints
  nuevos o seguiran ocultos en las rutas contractuales.

### 6.2 Worker de alertas

Pendiente principal:

- Crear o integrar un `alerts-worker`.

Flujo previsto:

1. Leer alertas activas desde MongoDB.
2. Evaluar si toca ejecutarlas segun `cron_expression`/`next_run_at`.
3. Buscar noticias nuevas en `rss_entradas` desde `last_checked_at`.
4. Comparar `descriptors` contra titulo/resumen.
5. Crear notificaciones en MongoDB.
6. Enviar correo si procede.
7. Actualizar `email_status`.
8. Actualizar `last_checked_at`, `last_run_at` y `next_run_at`.

### 6.3 Frontend

Pendientes relacionados:

- Gestionar la lista de descriptores aceptados por el usuario.
- Sugerir sinonimos/palabras relacionadas desde frontend, segun decision del
  equipo.
- Mostrar alertas usando el contrato publico actual.
- Mostrar notificaciones desde las rutas actuales o desde un futuro endpoint de
  buzon global.

## 7. Riesgos y observaciones

- El backend y el `rss-worker` usan actualmente nombres de colecciones RSS
  distintos en algunas partes (`information_sources`/`rss_channels` frente a
  `rss_fuentes`/`rss_entradas`). No se ha corregido en este trabajo para evitar
  un refactor amplio.
- Las colecciones nuevas no se han anadido a `RUNTIME_REQUIRED_COLLECTIONS`,
  para no impedir que el `rss-worker` actual arranque antes de que exista el
  worker de alertas.
- La API publica es prudente, pero los campos internos de Mongo ya preparan el
  producto real. Si el frontend necesita esos campos, conviene crear endpoints
  nuevos en vez de ampliar silenciosamente los modelos contractuales actuales.

## 8. Resumen ejecutivo

El estado actual es una base segura para continuar:

- Contrato publico conservado.
- Persistencia de alertas/notificaciones migrada a MongoDB.
- Campos internos preparados para procesamiento real.
- Bootstrap de Mongo actualizado.
- Roles de gestor/admin compatibles con el modelo Mongo actual.

El siguiente paso natural no es tocar mas el contrato actual, sino construir el
`alerts-worker` o endpoints nuevos especificos para buzon avanzado si el
frontend los necesita.
