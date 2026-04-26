# Workflow de Alertas y Notificaciones

Fecha: 2026-04-26

## 1. Objetivo

Este documento describe el flujo operativo real de alertas y notificaciones en el proyecto, apoyandose en las colecciones e indices MongoDB ya existentes.

## 2. Colecciones implicadas

### `alerts`

Campos usados en el workflow:

- `id`
- `user_id`
- `name`
- `descriptors`
- `categories`
- `cron_expression`
- `notification_channels`
- `enabled`
- `last_checked_at`
- `last_run_at`
- `next_run_at`
- `created_at`
- `updated_at`

Indice operativo clave:

- `idx_alerts_user_enabled_next_run`

Uso:

- permite consultar alertas activas pendientes de procesar sin barrer toda la coleccion

### `notifications`

Campos usados en el workflow:

- `id`
- `alert_id`
- `user_id`
- `timestamp`
- `subject`
- `metrics`
- `matches`
- `delivery_channels`
- `email_status`
- `email_sent_at`
- `email_error`
- `read_at`
- `created_at`
- `updated_at`

Indices operativos clave:

- `idx_notifications_alert_timestamp`
- `idx_notifications_user_read_timestamp`
- `idx_notifications_email_status_created`

Uso:

- consultas por alerta
- buzon global del usuario
- cola/outbox de emails pendientes

### `users`

Campos usados:

- `id`
- `email`
- `role`
- `role_ids`

Uso:

- resolver destinatario email
- control de acceso en API

### `rss_entradas`

Campos usados:

- `fecha_ingestion`
- `titulo`
- `resumen`
- `link`
- `hash_deduplicado`
- `id_fuente`
- `fecha_publicacion`

Uso:

- busqueda incremental de coincidencias desde `last_checked_at`

## 3. Componentes

### Backend

Responsabilidades:

- crear y actualizar alertas
- validar `cron_expression`
- persistir `next_run_at`
- exponer el contrato publico AG
- exponer endpoints de extension para configuracion de entrega y buzon

### RSS worker

Responsabilidades:

- ingerir feeds RSS
- persistir nuevas entradas en `rss_entradas`

### Alert worker

Responsabilidades:

- procesar alertas vencidas
- generar notificaciones
- enviar emails
- reintentar notificaciones pendientes con `email_status = pending`

## 4. Flujo principal

### Paso 1. Alta o actualizacion de alerta

1. El `backend` recibe `POST` o `PUT` de alerta.
2. Valida `cron_expression`.
3. Calcula `next_run_at` con `shared/utils/cron.py`.
4. Guarda la alerta en `alerts`.
5. La configuracion de canales se mantiene en `notification_channels`.

### Paso 2. Ingesta RSS

1. `rss-worker` recorre las fuentes activas.
2. Inserta nuevas noticias en `rss_entradas`.
3. La deduplicacion base sigue apoyandose en `hash_deduplicado`.

### Paso 3. Seleccion de alertas vencidas

1. `alert-worker` despierta cada `ALERT_WORKER_INTERVAL_SECONDS`.
2. Normaliza la hora actual a minuto.
3. Busca alertas con:

- `enabled = true`
- `next_run_at <= now`

4. Si una alerta activa no tiene `next_run_at`, la inicializa con su cron.

### Paso 4. Evaluacion de coincidencias

Para cada alerta vencida:

1. Se calcula la ventana de busqueda desde `last_checked_at`.
2. Si nunca se ha revisado, se usa `created_at`.
3. Se consultan `rss_entradas` con `fecha_ingestion > since`.
4. Se compara `descriptors` contra `titulo` y `resumen`.
5. Se evita duplicar una entrada ya notificada usando:

- `alert_id`
- `matches.rss_entry_hash`

### Paso 5. Creacion de la notificacion

Si hay coincidencias:

1. Se genera un nuevo ID persistente en `counters`.
2. Se crea un documento en `notifications`.
3. El documento incluye:

- asunto
- metricas
- coincidencias
- canales de entrega
- estado de email

4. Si el canal incluye `app`, ese mismo documento ya sirve de elemento de buzon.
5. Si el canal incluye `email`, el worker intenta enviarlo.

### Paso 6. Entrega de email

1. El worker resuelve el email del usuario en `users`.
2. Construye un cuerpo de correo con:

- alerta
- fecha de procesamiento
- lista de coincidencias
- resumen RSS
- enlace

3. Actualiza `notifications.email_status` a:

- `sent`
- `failed`
- `skipped`

4. Guarda tambien:

- `email_sent_at`
- `email_error`

### Paso 7. Actualizacion de estado de la alerta

Tras procesar una alerta:

- `last_checked_at = now`
- `last_run_at = now`
- `next_run_at = siguiente match del cron`
- `updated_at = now`

## 5. Outbox de notificaciones pendientes

Ademas del flujo principal, el `alert-worker` ejecuta una pasada sobre:

- `notifications.email_status = pending`

Esto sirve para:

- notificaciones creadas por API con canal `email`
- reanudacion tras reinicios del worker
- desacoplar persistencia y entrega

La consulta usa el indice `idx_notifications_email_status_created`.

## 6. API y vistas de datos

### Contrato publico conservado

- `Alert`
- `Notification`

No exponen configuracion de entrega ni detalles internos de la notificacion.

### Extensiones necesarias

Se anaden rutas especificas para:

- `GET/PUT /users/{user_id}/alerts/{alert_id}/notification-settings`
- `GET /users/{user_id}/notifications`
- `GET /users/{user_id}/notifications/{notification_id}`
- `PATCH /users/{user_id}/notifications/{notification_id}/read`

## 7. Razon de diseno

No se crean cron jobs del sistema por alerta.

Se ha optado por:

- cron persistido en BD
- worker continuo
- consulta incremental por `next_run_at`

Motivos:

- reinicios mas sencillos
- estado observable en MongoDB
- menos acoplamiento entre backend y worker
- mejor encaje con las tablas e indices ya creados

## 8. Riesgos conocidos

- Si en el futuro se lanzan varias replicas de `alert-worker`, convendra anadir un mecanismo atomico de claim para evitar carreras.
- La categoria operativa de alerta sigue apoyandose en `category_id`, pero el contrato publico actual expone `categories` por `code`/`label`; si se endurece esa parte, habra que cerrar la traduccion entre ambos niveles.
