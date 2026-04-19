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

Estado actualizado a 2026-04-20:

- Ya no es necesario crear de cero un `alerts-worker` para disponer de una
  primera version funcional.
- Se ha integrado un comprobador de alertas dentro del `rss-worker`, ejecutado
  al final de cada ciclo de ingesta RSS.
- La decision operativa actual es procesar alertas despues de insertar nuevas
  entradas en `rss_entradas`, usando MongoDB como punto de intercambio entre la
  API y el worker.

Flujo implementado:

1. Leer alertas activas desde MongoDB.
2. Buscar noticias nuevas en `rss_entradas` desde `last_checked_at`.
3. Si una alerta no tiene `last_checked_at`, usar una ventana inicial de 24
   horas para evitar revisar todo el historico.
4. Comparar `descriptors` contra `titulo` y `resumen` de cada entrada RSS.
5. Evitar duplicados comprobando si ya existe una notificacion para esa alerta
   con el mismo `matches.rss_entry_hash`.
6. Crear como maximo una notificacion por alerta y ciclo, agrupando todas las
   noticias coincidentes.
7. Guardar `matches`, `metrics`, `delivery_channels`, `email_status`,
   `subject`, `created_at` y `updated_at` en `notifications`.
8. Actualizar `last_checked_at`, `last_run_at` y `updated_at` en la alerta.

Archivos anadidos o modificados:

- `rss-worker/alerts/__init__.py`
- `rss-worker/alerts/matcher.py`
- `rss-worker/alerts/notifications.py`
- `rss-worker/alerts/processor.py`
- `rss-worker/worker/main.py`
- `rss-worker/tests/alerts/test_matcher.py`
- `rss-worker/tests/alerts/test_notifications.py`
- `rss-worker/tests/alerts/test_processor.py`
- `rss-worker/tests/worker/test_smoke.py`

Comportamiento relevante:

- El `rss-worker` llama a `process_alerts_safely(db)` justo despues de
  `fetch_de_entradas(db)`, tanto en modo `run_once` como en el bucle continuo.
- Los fallos de procesamiento de alertas se registran en logs, pero no tumban
  el ciclo principal de ingesta RSS.
- El asunto de la notificacion sigue el formato interno
  `Actualizacion de <alerta> en <YYYY-MM-DD HH:MM>`.
- El envio real de correo no se ejecuta todavia: si la alerta incluye `email`
  en `notification_channels`, la notificacion queda con `email_status:
  pending`; si no, queda como `skipped`.
- El matching actual es intencionadamente sencillo: busqueda case-insensitive
  por substring sobre titulo y resumen.

Validacion realizada:

```powershell
.\.venv\Scripts\python.exe -m pytest rss-worker/tests -q
```

Resultado: `14 passed`. Los avisos observados proceden de `.pytest_cache` y no
afectan al resultado funcional.

Pendientes del worker:

- Evaluar realmente `cron_expression`/`next_run_at`; ahora las alertas se
  comprueban al ritmo del ciclo RSS.
- Enviar correo real y actualizar `email_status` a `sent` o `failed`.
- Actualizar `next_run_at` si se adopta una libreria de cron.
- Filtrar por `category_id` y/o `rss_channel_ids` cuando la API exponga y
  rellene esos campos de forma fiable.
- Decidir si el comprobador debe permanecer dentro del `rss-worker` o extraerse
  mas adelante a un contenedor `alerts-worker` independiente.

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
- El procesamiento automatico de alertas ya existe en el `rss-worker`, pero aun
  no cubre cron real, envio SMTP, filtros por fuentes/categorias ni autorizacion
  fina de lectura/escritura en endpoints de la API.

## 8. Resumen ejecutivo

El estado actual es una base segura para continuar:

- Contrato publico conservado.
- Persistencia de alertas/notificaciones migrada a MongoDB.
- Campos internos preparados para procesamiento real.
- Bootstrap de Mongo actualizado.
- Roles de gestor/admin compatibles con el modelo Mongo actual.

El siguiente paso natural no es tocar mas el contrato actual, sino construir el
envio real de correo, endpoints nuevos especificos para buzon avanzado si el
frontend los necesita y validaciones/autorizacion mas estrictas en la API.

## 9. Actualizacion 2026-04-20 - Comprobador de alertas en RSS worker

El 2026-04-20 se ha implementado una primera version funcional del comprobador
de alertas dentro del `rss-worker`. Esta decision evita introducir un contenedor
nuevo en esta fase y aprovecha el punto natural del pipeline: justo despues de
actualizar las fuentes RSS y persistir nuevas entradas.

### 9.1 Encaje en el pipeline

El flujo efectivo queda asi:

1. La API registra alertas en MongoDB, coleccion `alerts`.
2. El `rss-worker` ingiere feeds y guarda noticias en `rss_entradas`.
3. Al terminar la ingesta, el `rss-worker` ejecuta el procesador de alertas.
4. El procesador busca coincidencias en noticias recientes.
5. Si hay coincidencias nuevas, crea documentos en `notifications`.
6. La API puede seguir leyendo las notificaciones desde sus endpoints actuales.

La comunicacion entre contenedores sigue siendo indirecta mediante MongoDB. No
se ha anadido socket, broker ni llamada HTTP entre backend y worker.

### 9.2 Diseno implementado

Se ha separado la funcionalidad en tres piezas:

- `matcher.py`: limpieza de descriptores y matching case-insensitive sobre
  `titulo` y `resumen`.
- `notifications.py`: construccion del documento interno de notificacion,
  incluyendo `subject`, `metrics`, `matches`, `delivery_channels` y
  `email_status`.
- `processor.py`: orquestacion sobre MongoDB, lectura de alertas activas,
  deduplicacion, creacion de notificaciones y actualizacion de marcas de la
  alerta.

La integracion en `worker/main.py` se ha hecho mediante `process_alerts_safely`.
La intencion es que un fallo de alertas no impida que continue la ingesta RSS.

### 9.3 Estado actual respecto a requisitos

Cubierto o parcialmente cubierto:

- Alertas persistidas en MongoDB.
- Notificaciones persistidas en MongoDB.
- Deteccion automatica de noticias por descriptor.
- Agrupacion de coincidencias en una notificacion por alerta y ciclo.
- Buzon interno preparado a nivel de datos (`notifications` con `user_id`,
  `read_at`, `matches`, `subject`).
- Preparacion de envio de email mediante `email_status: pending`.
- Deduplicacion basica por `alert_id` y `rss_entry_hash`.

Pendiente para poder considerar alertas/notificaciones practicamente cerradas
en backend:

- Integrar envio SMTP real usando la utilidad compartida de correo y actualizar
  `email_status`, `email_sent_at` y `email_error`.
- Crear endpoint de buzon global, recomendado:
  - `GET /api/v1/users/{user_id}/notifications`
  - `PATCH /api/v1/users/{user_id}/notifications/{notification_id}/read`
- Endurecer autorizacion: evitar que un usuario autenticado acceda o modifique
  alertas/notificaciones de otro usuario salvo que sea admin/gestor con permiso.
- Validar y usar `cron_expression`; ahora se procesa al ritmo del ciclo RSS.
- Resolver el uso real de `category_id` y `rss_channel_ids`.
- Implementar o decidir donde queda la recomendacion de 3 a 10 sinonimos o
  palabras relacionadas.
- Anadir test de integracion con Mongo real en Docker: alerta + entrada RSS
  coincidente debe crear una notificacion.
- Revisar la divergencia entre las colecciones usadas por la API de fuentes
  (`information_sources`/`rss_channels`) y las usadas por el worker
  (`rss_fuentes`/`rss_entradas`).

### 9.4 Valoracion

Con esta actualizacion, el backend deja de tener solo CRUD de alertas y pasa a
tener un workflow automatico minimo:

`alerta configurada -> entrada RSS ingerida -> coincidencia detectada ->
notificacion persistida`.

La parte de alertas/notificaciones queda bien encaminada para una v1 backend,
pero no debe marcarse como completamente terminada hasta cerrar al menos email
real, buzon global, autorizacion y una prueba de integracion con Mongo real.
