# Informe merge alertas notificaciones

Fecha: 2026-04-23

Rama origen: `origin/alerts-notifications`

Rama destino: `main`

## Estado del merge

El merge se ha ejecutado y los conflictos han quedado resueltos y preparados en el indice de Git.

No se ha creado todavia el commit final de merge, porque la aprobacion para ejecutar `git commit` fue rechazada. El repositorio queda en estado:

```text
All conflicts fixed but you are still merging.
use "git commit" to conclude merge
```

## Objetivo de la revision

La rama `alerts-notifications` introduce la persistencia y procesamiento de alertas y notificaciones sobre MongoDB. Durante la integracion habia que conservar esa parte, pero evitando que el merge consolidase la duplicacion de colecciones RSS detectada en `main`:

- Duplicacion no deseada: `information_sources` y `rss_channels`.
- Colecciones RSS canonicas que se han mantenido: `rss_fuentes` y `rss_entradas`.
- Colecciones nuevas necesarias para alertas: `alerts`, `notifications` y `counters`.

## Conflictos resueltos

Se resolvieron conflictos en:

- `.github/workflows/main.yml`
- `docker-compose.yml`
- `rss-worker/worker/main.py`
- `shared/mongo/__init__.py`
- `shared/mongo/bootstrap_spec.py`

### CI

En `.github/workflows/main.yml` se combinaron las dos aportaciones:

- Se mantiene la verificacion de que no exista un `.env` real en el repositorio.
- Se crea el `.env` temporal desde `.env.example`.
- Se conserva la espera activa al healthcheck del backend, mas robusta que un `sleep` fijo.
- Se mantiene la ejecucion de `pytest tests/` dentro de `newsradar-backend`.

### Docker Compose

En `docker-compose.yml` el conflicto era solo de formato en un bloque comentado de Elasticsearch. Se mantuvo la version limpia del bloque comentado.

### Worker RSS

En `rss-worker/worker/main.py` se integraron las dos lineas de trabajo:

- Se conserva la API interna `/fuentes` del worker, que escribe en `rss_fuentes`.
- Se incorpora `process_alerts` para ejecutar alertas despues de cada ciclo de ingesta RSS.
- Se añade `process_alerts_safely()` para que un fallo en alertas no tumbe la ingesta.
- Se añade `run_preflight()` para validar colecciones e indices requeridos.
- Se corrige el bug existente:

```python
if fuente.activo == False:
    pass
```

Ahora las fuentes inactivas se omiten realmente:

```python
if fuente.activo is False:
    continue
```

## Cambios necesarios respecto a lo que habia en main

### 1. Alertas y notificaciones pasan a MongoDB

La rama ya migraba la funcionalidad de alertas y notificaciones desde stores en memoria a MongoDB. Se ha mantenido esa direccion.

Cambios principales:

- `backend/app/alertas/routes.py` usa `alerts_col`.
- `backend/app/notificaciones/routes.py` usa `notifications_col`.
- `backend/app/store.py` expone `alerts_col`, `notifications_col` y `counters_col`.
- Los IDs de alertas y notificaciones se generan con `next_mongo_id()`.
- El worker crea notificaciones agrupando entradas RSS que hacen match con los descriptores de una alerta.

Esto mantiene las librerias y modulos desarrollados para alertas:

- `rss-worker/alerts/matcher.py`
- `rss-worker/alerts/notifications.py`
- `rss-worker/alerts/processor.py`

### 2. Se elimina el uso runtime de las colecciones RSS duplicadas

En `main`, las rutas RSS del backend escribian en:

- `information_sources`
- `rss_channels`

Eso duplicaba la configuracion RSS, porque el worker solo procesa:

- `rss_fuentes`
- `rss_entradas`

Durante el merge se ha cambiado `backend/app/rss/routes.py` para que las rutas del contrato API sigan existiendo, pero persistan sobre `rss_fuentes`.

Las rutas conservadas son:

- `GET /api/v1/information-sources`
- `POST /api/v1/information-sources`
- `GET /api/v1/information-sources/{source_id}`
- `PUT /api/v1/information-sources/{source_id}`
- `DELETE /api/v1/information-sources/{source_id}`
- `GET /api/v1/information-sources/{source_id}/rss-channels`
- `POST /api/v1/information-sources/{source_id}/rss-channels`
- `GET /api/v1/information-sources/{source_id}/rss-channels/{channel_id}`
- `PUT /api/v1/information-sources/{source_id}/rss-channels/{channel_id}`
- `DELETE /api/v1/information-sources/{source_id}/rss-channels/{channel_id}`

Internamente ahora se guardan documentos en `rss_fuentes` con:

- `tipo = "source"` para fuentes de informacion del contrato.
- `tipo = "channel"` para canales RSS procesables por el worker.

### 3. `rss_fuentes` se amplia para soportar el contrato API

Se han añadido campos compatibles con el contrato de fuentes y canales:

- `tipo`
- `source_id`
- `source_name`
- `source_url`
- `channel_id`
- `category_id`
- `deleted_at`

Se mantiene la compatibilidad con el modelo operativo del worker:

- `hash_fuente`
- `medio`
- `rss`
- `url`
- `activo`
- `categoria_iptc`
- `creado`
- `actualizado`

El worker filtra ahora en `ColeccionRssFuentes.lista_fuentes()`:

- canales activos (`activo = true`),
- documentos `tipo = "channel"`,
- y documentos antiguos sin `tipo`, para no romper datos ya existentes.

### 4. Borrado logico de canales RSS

Para evitar romper referencias historicas desde `rss_entradas.id_fuente` hacia `rss_fuentes._id`, el borrado de canales del contrato API no elimina fisicamente el documento de `rss_fuentes`.

Ahora se marca:

- `activo = false`
- `deleted_at = fecha`
- `actualizado = fecha`

Asi el worker deja de procesarlo, pero las entradas historicas no quedan apuntando a un documento inexistente.

### 5. Categorias consultan los canales en `rss_fuentes`

`backend/app/category/routes.py` ya no consulta `rss_channels_store` para saber si una categoria esta asociada a canales RSS.

Ahora consulta `rss_fuentes_col` buscando documentos:

- `tipo = "channel"`
- `category_id = <categoria>`
- no borrados logicamente

### 6. Bootstrap Mongo unificado

Se incorporo `shared/mongo/bootstrap_spec.py` y se ajusto `scripts/mongo/init-mongo.js`.

El bootstrap ahora contempla:

- `rss_fuentes`
- `rss_entradas`
- `rss_entradas_raw`
- `users`
- `user_sessions`
- `alerts`
- `notifications`
- `counters`

No se añaden `information_sources` ni `rss_channels` como colecciones nuevas.

Los contadores persistentes incluyen:

- `information_sources`
- `rss_channels`
- `alerts`
- `notifications`

Estos dos primeros son contadores de IDs del contrato API, no colecciones RSS separadas.

### 7. Preflight del worker

El worker valida al arrancar que existan colecciones e indices requeridos.

Para soportarlo se añadio:

- `Database.ping()`
- exports de `RUNTIME_REQUIRED_COLLECTIONS` y `RUNTIME_REQUIRED_INDEXES` en `shared/mongo/__init__.py`

## Cambios de la rama que se han conservado

Se ha mantenido la funcionalidad principal de `alerts-notifications`:

- Modelos de alertas con `enabled`.
- CRUD de alertas persistido en MongoDB.
- CRUD de notificaciones persistido en MongoDB.
- Usuarios por defecto de seed para `admin`, `manager` y `reader`.
- Ajustes de autenticacion para campos `role` y `status`.
- Procesador de alertas en el worker RSS.
- Generacion de notificaciones agrupadas por alerta y ciclo.
- Pruebas de matcher, notificaciones y procesador.
- Cambios de frontend en `AuthContext` y `AlertsPage`.

## Comprobaciones realizadas

### Compilacion Python

Ejecutado en local:

```text
python -m compileall backend/app shared rss-worker/alerts rss-worker/rss rss-worker/worker
```

Resultado: correcto.

### Pruebas backend en contenedor

Ejecutado en `newsradar-backend`:

```text
docker exec -w /app -e PYTHONPATH=/app:/app/backend newsradar-backend pytest backend/tests/test_seed_data.py backend/tests/test_alertas.py backend/tests/test_rss.py
```

Resultado:

```text
6 passed
```

### Pruebas worker en contenedor temporal

Ejecutado montando el workspace actual:

```text
docker run --rm -v "${PWD}:/app" -w /app -e PYTHONPATH=/app:/app/backend:/app/rss-worker newsradar-g5-2026-backend pytest rss-worker/tests/alerts rss-worker/tests/worker/test_smoke.py
```

Resultado:

```text
15 passed
```

### Validaciones Git

Ejecutado:

```text
git diff --cached --check
```

Resultado: sin errores.

Tambien se comprobo que no quedan marcadores de conflicto ni usos runtime de:

- `sources_col`
- `channels_col`
- `information_sources_store`
- `rss_channels_store`
- `db["information_sources"]`
- `db["rss_channels"]`

Excepcion: `backend/app/api_ag_comentado.py`, que es un archivo de referencia comentado y no forma parte del runtime.

## Riesgos y puntos pendientes

### Migracion de datos existentes

Si ya existen documentos en `information_sources` y `rss_channels` en una base local o de despliegue, este merge deja de usarlos en runtime, pero no migra esos datos automaticamente.

Queda pendiente una migracion que:

- lea `information_sources` y `rss_channels`,
- deduplique registros,
- los inserte o actualice en `rss_fuentes`,
- y opcionalmente archive o elimine las colecciones antiguas.

### Bootstrap sobre bases ya existentes

Si el volumen de MongoDB ya existia antes de este merge, `init-mongo.js` no se reaplica automaticamente por Docker.

Para asegurar las nuevas colecciones e indices de alertas/notificaciones/counters, hay que ejecutar:

```text
docker exec newsradar-backend python /app/scripts/mongo/admin/apply_bootstrap.py
```

### Reutilizacion de URLs borradas logicamente

Los canales RSS se borran logicamente para no romper referencias historicas de `rss_entradas`.

Como `rss_fuentes.url` tiene indice unico, re-crear despues un canal con la misma URL puede requerir una decision adicional:

- reactivar el documento existente,
- o relajar el indice unico con una estrategia parcial para documentos no borrados.

## Conclusion

El merge ha requerido algo mas que resolver conflictos mecanicos. La parte de alertas/notificaciones se ha conservado, pero se ha aprovechado la integracion para evitar consolidar la duplicacion RSS existente en `main`.

El resultado deja:

- Alertas y notificaciones en MongoDB mediante `alerts`, `notifications` y `counters`.
- Fuentes y canales RSS del contrato API sobre `rss_fuentes`.
- El worker leyendo solo canales activos y no fuentes contractuales.
- El merge resuelto y testeado, pendiente solo del commit final.
