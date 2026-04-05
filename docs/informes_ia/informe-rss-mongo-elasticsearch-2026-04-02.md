# Informe tecnico - Unificacion RSS MongoDB y Elasticsearch

Fecha: 02/04/2026

## 1. Objetivo

Dejar operativo el conector RSS -> MongoDB y preparado el conector MongoDB -> Elasticsearch para comenzar la carga y almacenamiento de noticias RSS en ambas bases de datos, alineando los modelos con el codigo RSS existente.

## 2. Decisiones aplicadas

1. Se mantienen los campos en espanol en el modelo RSS (`titulo`, `autores`, `categorias`, `fecha_publicacion`, etc.).
2. MongoDB usa `_id` nativo `ObjectId` como identificador tecnico.
3. Se conservan hashes personalizados para identidad logica/deduplicacion:
   - `hash_fuente` en `rss_fuentes`.
   - `hash_deduplicado` en `rss_entradas`.

## 3. Cambios implementados

### 3.1 Capa RSS (backend/src/rss)

- `RSSFeedSource.a_mongo()`:
  - ya no fuerza `_id` con hash.
  - guarda `hash_fuente`.
  - incluye `activo`.
  - anade `mongo_id` en memoria para enlazar entradas con ObjectId real.

- `RSSEntrada`:
  - `id_fuente` pasa a persistirse como `ObjectId` (via `fuente.mongo_id`).
  - mantiene `hash_deduplicado`.
  - se anade campo opcional `resumen`.

- `RSSParser`:
  - extrae `summary/description` en `resumen`.

### 3.2 Capa Mongo Python (backend/src/mongo)

- `Coleccion`:
  - ahora aplica esquema y crea indices al inicializar.

- `ColeccionRssFuentes`:
  - esquema alineado a campos en espanol.
  - upsert idempotente por `hash_fuente`.
  - devuelve/asigna `ObjectId` a `fuente.mongo_id`.

- `ColeccionRssEntradas`:
  - esquema con `id_fuente: objectId`.
  - arreglo de incoherencias de nombres (`categorias` en lugar de `categories`).
  - insercion idempotente por `hash_deduplicado`.
  - indices por hash, fuente+fecha, fecha y categorias.

- Nueva coleccion `ColeccionRssEntradasRaw`:
  - para conservar payload original de RSS cuando sea necesario.
  - indices por `id_entrada` y `id_fuente+fecha_captura`.

- `Database`:
  - conexion por `MONGODB_URI` (o fallback con variables de entorno).
  - se elimina la creacion de usuarios desde la app (queda en bootstrap de Mongo).
  - se registra `col_rss_entradas_raw`.

### 3.3 Bootstrap Mongo (docker/mongo/init-mongo.sh)

Se unifica el contrato RSS con nombres en espanol:

- Colecciones RSS:
  - `rss_fuentes`
  - `rss_entradas`
  - `rss_entradas_raw`

- Validadores e indices actualizados para:
  - `ObjectId` tecnico en referencias.
  - hashes logicos (`hash_fuente`, `hash_deduplicado`).
  - busquedas y agregaciones por categoria y fecha.

### 3.4 Elasticsearch

- Nuevo bootstrap de indices: `docker/elasticsearch/init-elasticsearch.sh`.
- Nuevo servicio en Compose: `elasticsearch-setup` (one-shot) para crear indices si no existen.
- Indices creados:
  - `rss_entradas_idx`
  - `rss_fuentes_idx`
- Mappings orientados a:
  - full-text de `titulo` y `resumen`.
  - agregaciones por `categorias`, `medio` y fechas.

Razon de diseno:

- En MongoDB se usa bootstrap nativo por `docker-entrypoint-initdb.d`.
- En Elasticsearch la imagen oficial no ofrece un mecanismo equivalente para crear indices/mappings automaticamente en primer arranque.
- Por eso se adopta un contenedor auxiliar one-shot (`elasticsearch-setup`) que ejecuta una inicializacion idempotente y repetible.

### 3.5 Conector Mongo -> Elasticsearch

- Nuevo script: `backend/scripts/rss_mongo_to_elasticsearch.py`.
- Funcionalidad:
  - lee `rss_fuentes` y `rss_entradas` de Mongo.
  - indexa por bulk en Elasticsearch.
  - idempotencia en entradas usando `hash_deduplicado` como `_id` en ES.

## 4. Motivacion de los cambios

1. Eliminar inconsistencias entre contrato Python RSS y bootstrap de Mongo.
2. Asegurar referencias robustas entre entidades con `ObjectId` real.
3. Mantener deduplicacion estable y reproducible con hashes propios.
4. Dejar Elasticsearch listo para paneles, tendencias y busquedas textuales.

## 5. Impacto esperado

- Se facilita el flujo end-to-end de ingesta RSS.
- Se reduce el riesgo de errores por esquemas desalineados.
- Se habilita una base solida para estadisticas y visualizacion.

## 6. Verificaciones recomendadas tras despliegue

1. Reinicializar stack con datos vacios si se desea aplicar bootstrap desde cero.
2. Verificar en Mongo la existencia de colecciones e indices RSS.
3. Ejecutar ingesta RSS de prueba y validar deduplicacion por hash.
4. Ejecutar `rss_mongo_to_elasticsearch.py` y comprobar documentos en indices ES.

## 7. ADR

Si, se recomienda documentar esta decision en ADR porque cambia el contrato de datos RSS y la politica de identificadores:

- `ObjectId` tecnico en Mongo.
- hashes logicos para identidad funcional y deduplicacion.
- mantenimiento de nomenclatura de campos en espanol.
