# Informe: duplicacion de colecciones RSS en MongoDB

Fecha: 2026-04-23

## Resumen ejecutivo

Actualmente existen dos modelos de datos para representar fuentes y canales RSS:

- Modelo operativo del `rss-worker`: `rss_fuentes` y `rss_entradas`.
- Modelo usado por el backend para el contrato API: `information_sources` y `rss_channels`.

La duplicacion problematica esta entre `rss_fuentes` y el par `information_sources`/`rss_channels`. No hay evidencia de que `rss_entradas` sea una duplicacion funcional de `rss_channels`: `rss_entradas` contiene noticias/articulos ingeridos, no fuentes ni canales configurables.

El efecto practico es que una fuente creada por la API REST del backend puede quedar almacenada en `information_sources`/`rss_channels`, pero el worker RSS no la procesa porque solo lee `rss_fuentes`.

## Estado observado en MongoDB

Consulta realizada contra el contenedor local `newsradar-mongodb`:

```text
information_sources 2
rss_channels 2
rss_entradas 457
rss_fuentes 10
stats 0
user_sessions 0
users 1
```

Ademas, se observaron documentos repetidos dentro de las colecciones creadas por el backend:

```javascript
// information_sources
{ id: 1, name: "El Mundo", url: "https://www.elmundo.es/" }
{ id: 1, name: "El Mundo", url: "https://www.elmundo.es/" }

// rss_channels
{
  id: 1,
  information_source_id: 1,
  url: "https://www.elmundo.es/rss/portada.xml",
  category_id: 1
}
{
  id: 1,
  information_source_id: 1,
  url: "https://www.elmundo.es/rss/portada.xml",
  category_id: 1
}
```

Esto muestra dos problemas distintos:

1. Existen colecciones paralelas para representar configuracion RSS.
2. Las colecciones `information_sources` y `rss_channels` permiten duplicados porque no tienen indices unicos ni validadores.

## Colecciones consideradas correctas

Se toman como colecciones canonicas:

- `rss_fuentes`: catalogo operativo de feeds RSS que debe leer el worker.
- `rss_entradas`: noticias/articulos obtenidos desde esos feeds.

El contrato de la API debe mantenerse, pero su implementacion no deberia persistir en colecciones separadas si se decide que `rss_fuentes` es la fuente de verdad.

## Evidencias en codigo

### Modelo canonico usado por el worker

`rss_fuentes` esta definida en:

- `shared/mongo/colecciones/ColeccionRssFuentes.py`

Linea relevante:

```python
NOMBRE_COLECCION = "rss_fuentes"
```

Campos actuales:

```text
hash_fuente
medio
rss
url
activo
categoria_iptc
creado
actualizado
```

El worker lee fuentes desde `rss_fuentes`:

```python
fuentes: list[RSSFuente] = db.col_rss_fuentes.lista_fuentes()
```

Archivo:

- `rss-worker/worker/main.py`

Tambien inserta fuentes estandar en esa coleccion:

```python
for feed in generar_lista_estandar_feeds():
    db.col_rss_fuentes.insertar(feed)
```

La API interna del worker `/fuentes` tambien escribe en `rss_fuentes`:

```python
get_db().col_rss_fuentes.insertar(objecto_fuente)
```

Archivo:

- `rss-worker/worker/api_fuentes.py`

### `rss_entradas` no es catalogo de canales

`rss_entradas` esta definida en:

- `shared/mongo/colecciones/ColeccionRssEntradas.py`

Linea relevante:

```python
NOMBRE_COLECCION = "rss_entradas"
```

Campos principales:

```text
id_fuente
titulo
autores
link
categorias
categorias_raw
resumen
fecha_publicacion
hash_deduplicado
fecha_ingestion
```

La relacion con `rss_fuentes` se hace por ObjectId:

```python
id_fuente = self._db_padre.col_rss_fuentes._collection.find_one({"url": url_fuente})
datos["id_fuente"] = id_fuente["_id"]
```

Por tanto, `rss_entradas` depende de `rss_fuentes` y no reemplaza a `rss_channels`.

### Colecciones paralelas creadas por el backend

El backend declara colecciones separadas en:

- `backend/app/store.py`

Lineas relevantes:

```python
sources_col = db["information_sources"]
channels_col = db["rss_channels"]
```

MongoDB no crea una coleccion solo por evaluar `db["nombre"]`; la crea cuando se realiza la primera escritura.

Las escrituras que materializan estas colecciones estan en:

- `backend/app/rss/routes.py`

Para `information_sources`:

```python
sources_col.insert_one(new_source)
```

Para `rss_channels`:

```python
channels_col.insert_one(new_channel)
```

Estas rutas implementan el contrato HTTP, pero no alimentan al worker.

## Diferencias de esquema

### `InformationSource` del contrato API

Segun `docs/contrato-api-backend.md`:

```json
{
  "id": 1,
  "name": "El Pais",
  "url": "https://elpais.com"
}
```

### `RSSChannel` del contrato API

```json
{
  "id": 1,
  "information_source_id": 1,
  "url": "https://elpais.com/rss",
  "category_id": 2
}
```

### `rss_fuentes` actual

```json
{
  "hash_fuente": "...",
  "medio": "el_pais",
  "rss": "",
  "url": "https://feeds.elpais.com/...",
  "activo": true,
  "categoria_iptc": "Politica",
  "creado": "...",
  "actualizado": "..."
}
```

El modelo `rss_fuentes` actual se parece mas a un canal RSS operativo que a una fuente de informacion contractual. Por eso, para cumplir completamente el contrato usando solo `rss_fuentes`, hace falta ampliar o adaptar el esquema.

## Impacto funcional

### Alta de fuentes desde backend

Si un usuario crea una fuente con:

```text
POST /api/v1/information-sources
POST /api/v1/information-sources/{source_id}/rss-channels
```

los datos quedan en:

```text
information_sources
rss_channels
```

Pero el worker solo lee:

```text
rss_fuentes
```

Resultado: el canal creado por la API no entra en la ingesta RSS.

### Alta de fuentes desde worker

Si se usa la API interna del worker:

```text
POST /fuentes
```

los datos quedan en:

```text
rss_fuentes
```

Resultado: el worker puede procesarlos, pero esa alta no queda representada como `InformationSource`/`RSSChannel` en las colecciones del backend.

### Categorias

El contrato de `RSSChannel` exige `category_id`.

El modelo `rss_fuentes` actual usa:

```text
categoria_iptc
```

Esto es un string canonico o descriptivo, no un identificador numerico compatible directamente con `category_id`.

Para cumplir completamente el contrato, hay que decidir una estrategia:

- Guardar `category_id` en `rss_fuentes`.
- Mantener `categoria_iptc` como campo derivado o legado.
- O mapear `category_id` contra categorias IPTC en tiempo de respuesta.

La opcion mas clara es persistir `category_id` y conservar `categoria_iptc` solo si sigue siendo util para el worker.

## Origen historico

### Creacion del modelo API en memoria

Commit:

```text
6fc726684b57cc270d0c154a57fa3a1c8fdd42dd
Autor: Ignacio <100495680@alumnos.uc3m.es>
Fecha: 2026-04-15 09:42:12 +0200
Mensaje: add: organizacion de las clases y api's del backend
```

Este commit introduce los modelos y rutas `InformationSource`/`RSSChannel`, pero inicialmente trabajan contra stores en memoria.

No es el commit que crea colecciones duplicadas en MongoDB.

### Introduccion de colecciones Mongo separadas

Commit responsable de la duplicacion persistida:

```text
764a9f93d05cec27ac446b4d80b217ae7e1f9b27
Autor: 100495927 <100495927@alumnos.uc3m.es>
Fecha: 2026-04-17 18:36:14 +0200
Mensaje: tests
```

Este commit cambia las rutas del backend para usar:

```python
sources_col = db["information_sources"]
channels_col = db["rss_channels"]
```

y reemplaza operaciones en memoria por operaciones PyMongo.

### Modelo RSS previo

El modelo `rss_fuentes`/`rss_entradas` ya existia como base del worker y del bootstrap Mongo.

El bootstrap oficial crea:

```text
rss_fuentes
rss_entradas
users
user_sessions
```

Archivo:

- `scripts/mongo/init-mongo.js`

No crea:

```text
information_sources
rss_channels
```

## Causa de documentos duplicados exactos

Ademas de la duplicacion de colecciones, se han generado documentos duplicados dentro de `information_sources` y `rss_channels`.

La causa probable es:

- `next_id()` usa contadores en memoria en `backend/app/store.py`.
- Al reiniciar procesos o ejecutar tests, el contador vuelve a empezar en `1`.
- `information_sources` y `rss_channels` no tienen indices unicos.
- `backend/tests/test_rss.py` inserta siempre `El Mundo` y su canal RSS.

Fragmento del test:

```python
source_data = {"name": "El Mundo", "url": "https://www.elmundo.es"}
source_resp = client.post("/api/v1/information-sources", json=source_data, headers=auth_headers)

rss_data = {"url": "https://www.elmundo.es/rss/portada.xml", "category_id": cat_id}
rss_resp = client.post(
    f"/api/v1/information-sources/{source_id}/rss-channels",
    json=rss_data,
    headers=auth_headers,
)
```

Esto explica por que existen dos documentos identicos con `id: 1`.

## Se puede cumplir el contrato usando solo `rss_fuentes`?

Si, pero no con el esquema actual sin adaptacion.

Para cumplir completamente el contrato, `rss_fuentes` debe poder representar:

1. Fuentes de informacion.
2. Canales RSS asociados a esas fuentes.
3. Identificadores enteros estables compatibles con la API.
4. Relacion `source_id` -> canales.
5. `category_id` para canales RSS.
6. Estado operativo para el worker (`activo`).
7. Deduplicacion por URL/hash.

## Propuesta de unificacion

Mantener el contrato HTTP:

```text
/api/v1/information-sources
/api/v1/information-sources/{source_id}/rss-channels
```

pero implementar esas rutas sobre `rss_fuentes`.

### Campos recomendados para `rss_fuentes`

```text
source_id: int
source_name: string
source_url: string
channel_id: int | null
channel_url: string | null
category_id: int | null
hash_fuente: string
medio: string
rss: string | null
url: string
activo: bool
categoria_iptc: string | null
creado: date
actualizado: date
tipo: "source" | "channel"
```

Una alternativa mas simple es guardar solo documentos de tipo canal y derivar las fuentes agrupando por `source_id`, pero eso no permite representar una fuente sin canales. Como el contrato permite crear primero una `InformationSource` y despues crear canales, conviene permitir documentos tipo `source`.

### Mapeo API recomendado

#### `POST /api/v1/information-sources`

Crear documento en `rss_fuentes`:

```text
tipo = "source"
source_id = nuevo id estable
source_name = payload.name
source_url = payload.url
activo = true
```

Responder:

```json
{
  "id": source_id,
  "name": source_name,
  "url": source_url
}
```

#### `POST /api/v1/information-sources/{source_id}/rss-channels`

Crear documento en `rss_fuentes`:

```text
tipo = "channel"
source_id = source_id
source_name = nombre de la fuente
source_url = url de la fuente
channel_id = nuevo id estable
channel_url = payload.url
url = payload.url
rss = payload.url
category_id = payload.category_id
activo = true
```

Responder:

```json
{
  "id": channel_id,
  "information_source_id": source_id,
  "url": channel_url,
  "category_id": category_id
}
```

#### `GET /api/v1/information-sources`

Leer documentos `tipo = "source"` o agrupar documentos por `source_id`.

#### `GET /api/v1/information-sources/{source_id}/rss-channels`

Leer documentos `tipo = "channel"` con `source_id`.

#### `DELETE /api/v1/information-sources/{source_id}`

Borrar:

```text
tipo = "source" con source_id
tipo = "channel" con source_id
```

Antes de borrar canales conviene valorar el impacto sobre `rss_entradas`, porque las entradas historicas referencian `rss_fuentes._id`.

## Riesgos y puntos a corregir

### 1. Referencias desde `rss_entradas`

`rss_entradas.id_fuente` guarda ObjectId de `rss_fuentes`.

Si se borra fisicamente un canal de `rss_fuentes`, las entradas historicas quedan con una referencia a un documento inexistente.

Opciones:

- Borrado logico: `activo = false`.
- Mantener documentos de canal aunque se eliminen del contrato API.
- Migrar entradas historicas si se hace borrado fisico.

Recomendacion: usar borrado logico para canales RSS ya procesados.

### 2. Worker debe filtrar documentos

Si `rss_fuentes` contiene documentos tipo `source`, el worker debe procesar solo:

```text
tipo = "channel"
activo = true
```

Ademas, actualmente hay un bug en el worker:

```python
if fuente.activo == False:
    pass
```

Eso no omite la fuente. Debe ser:

```python
if fuente.activo is False:
    continue
```

### 3. Contadores en memoria

`next_id()` no es valido para persistencia real porque se reinicia con el proceso.

Hay que sustituirlo por:

- coleccion `counters` en Mongo con incremento atomico, o
- ObjectId en Mongo y adaptador a string si se ajusta el contrato, o
- indice unico con generacion transaccional/atomica.

Como el contrato usa `int`, la mejor opcion es una coleccion `counters`.

### 4. Validadores e indices

`information_sources` y `rss_channels` no tienen validadores ni indices.

Si se eliminan, `rss_fuentes` debe reforzarse con indices:

```text
source_id unique para documentos tipo source
channel_id unique para documentos tipo channel
url unique para canales activos
hash_fuente unique
source_id + channel_id
source_id + tipo
activo
```

### 5. Categoria IPTC

El contrato usa `category_id`; el worker usa `categoria_iptc` como fallback de normalizacion.

Hay que alinear ambos mundos:

- Persistir `category_id` para cumplir API.
- Calcular o guardar `categoria_iptc` para el worker.
- Asegurar que `ensure_category_exists(category_id)` valida contra categorias reales.

## Recomendacion final

La direccion recomendada es:

1. Declarar `rss_fuentes` y `rss_entradas` como unicas colecciones RSS canonicas.
2. Eliminar el uso runtime de `information_sources` y `rss_channels`.
3. Mantener intactas las rutas del contrato API.
4. Reimplementar esas rutas sobre `rss_fuentes`.
5. Ampliar el esquema de `rss_fuentes` para soportar `source_id`, `channel_id`, `category_id` y relacion fuente-canal.
6. Cambiar el worker para leer solo canales activos desde `rss_fuentes`.
7. Sustituir `next_id()` por contadores persistentes en Mongo.
8. Crear una migracion que:
   - lea `information_sources` y `rss_channels`,
   - los inserte/upsertee en `rss_fuentes`,
   - elimine duplicados exactos,
   - deje de usar las colecciones antiguas.

## Decision pendiente

Antes de implementar la unificacion hay que decidir si se quiere:

1. Mantener documentos `tipo = "source"` y `tipo = "channel"` dentro de `rss_fuentes`.
2. Guardar solo canales en `rss_fuentes` y derivar fuentes agrupando.

Para cumplir el contrato completamente, especialmente crear una fuente antes de crear canales, la opcion 1 es mas robusta.
