# Gestión real de categorías en el backend

## Objetivo

El objetivo fue cerrar correctamente el CRUD de categorías en el backend de NewsRadar con cambios mínimos, manteniendo los contratos públicos existentes y sin tocar el frontend.

La necesidad principal era que `POST /api/v1/categories` y `PUT /api/v1/categories/{category_id}` dejaran de ser endpoints de compatibilidad sin persistencia real, y que el ciclo completo de categorías mantuviera la integridad referencial con los canales RSS.

## Qué se revisó

Se revisaron los puntos indicados antes de modificar código:

- `backend/app/category/routes.py`
- `backend/app/category/models.py`
- `backend/app/app.py`
- `backend/app/store.py`
- `backend/app/rss/routes.py`
- `shared/iptc_catalog.py`
- Tests existentes relacionados con categorías, seed data y RSS

## Qué ya funcionaba

Antes del cambio ya había varias piezas correctas:

- `GET /api/v1/categories` listaba las categorías cargadas en `categories_store`.
- `GET /api/v1/categories/{category_id}` devolvía una categoría existente o `404`.
- La carga inicial se hacía en `create_seed_data()`, leyendo `rss_categorias_iptc` desde MongoDB.
- Si la colección de categorías estaba vacía, el sistema hacía fallback al catálogo IPTC estático de `shared/iptc_catalog.py`.
- Al crear un canal RSS, `backend/app/rss/routes.py` validaba que `category_id` existiera mediante `ensure_category_exists`.
- Al actualizar un canal RSS, también se validaba que la nueva categoría existiera.
- `DELETE /api/v1/categories/{category_id}` ya comprobaba si había canales RSS activos asociados y devolvía `409` en ese caso.

## Qué faltaba

Lo que faltaba era la gestión real de persistencia:

- `POST /api/v1/categories` no persistía categorías.
- `POST /api/v1/categories` podía devolver una categoría falsa con `id=-1`.
- `PUT /api/v1/categories/{category_id}` no persistía cambios.
- `PUT` podía aparentar actualizar una categoría inexistente.
- `DELETE` no devolvía `404` si la categoría no existía.
- `DELETE` no eliminaba realmente la categoría de Mongo ni de `categories_store`.
- No había validación real de duplicados por nombre normalizado.

## Cambios realizados

### `backend/app/category/routes.py`

Se convirtió el CRUD de categorías en una implementación real usando MongoDB y manteniendo sincronizado el store en memoria.

Se añadieron helpers internos para:

- Obtener la fecha actual en UTC.
- Normalizar nombres de categoría eliminando diferencias de mayúsculas, espacios repetidos y acentos.
- Validar que no exista otra categoría con el mismo nombre normalizado.
- Construir documentos compatibles con la colección `rss_categorias_iptc`.
- Generar un ID nuevo con `next_mongo_id("categories")`, evitando colisiones con IDs ya cargados.

El endpoint `POST /categories` ahora:

- Resuelve primero el nombre contra el catálogo IPTC con `resolve_category`.
- Si el nombre corresponde a IPTC y el ID ya existe, devuelve `409`.
- Si no corresponde a IPTC, crea una categoría nueva con un ID generado por Mongo.
- Rechaza duplicados por nombre normalizado.
- Inserta el documento en `rss_categorias_iptc`.
- Actualiza `categories_store`.
- Ya no devuelve nunca una categoría falsa con `id=-1`.

El endpoint `PUT /categories/{category_id}` ahora:

- Devuelve `404` si la categoría no existe.
- Mantiene el mismo ID de categoría, para no romper canales RSS existentes.
- Valida duplicados por nombre normalizado.
- Persiste el cambio en `rss_categorias_iptc`.
- Actualiza `categories_store`.

El endpoint `DELETE /categories/{category_id}` ahora:

- Devuelve `404` si la categoría no existe.
- Devuelve `409` si hay canales RSS activos asociados.
- Si no está en uso, elimina la categoría de MongoDB.
- También la elimina de `categories_store`.

### `backend/app/app.py`

Se ajustó la carga inicial de categorías desde Mongo para ignorar documentos con `deleted_at`.

Aunque el borrado actual elimina físicamente el documento, este filtro deja el loader preparado para no recargar categorías marcadas como eliminadas si en algún momento se usara borrado lógico en esa colección.

### `backend/tests/test_api_features.py`

Se actualizaron y añadieron tests focalizados para la lógica afectada:

- Crear una categoría nueva y persistirla.
- Rechazar duplicados por nombre normalizado en `POST`.
- Listar categorías cargadas.
- Actualizar y persistir una categoría existente.
- Devolver `404` al actualizar una categoría inexistente.
- Rechazar duplicados por nombre normalizado en `PUT`.
- Devolver `409` al borrar una categoría asociada a canales RSS activos.
- Devolver `404` al borrar una categoría inexistente.
- Borrar una categoría sin canales asociados.
- Rechazar creación de canal RSS con categoría inexistente.
- Rechazar actualización de canal RSS hacia categoría inexistente.

## Por qué se hizo así

Se eligió esta solución porque respeta la arquitectura actual del proyecto:

- MongoDB ya era la fuente persistente para `rss_categorias_iptc`.
- `categories_store` ya se usaba para validaciones rápidas en runtime.
- `ensure_category_exists` ya era el punto común usado por RSS.
- La forma documental existente de categorías usaba `_id` y `descripciones`, por lo que se mantuvo esa estructura.
- No se modificó `shared/iptc_catalog.py`, para no romper la normalización IPTC ni la resolución canónica existente.
- No se tocó el frontend.
- No se cambiaron nombres de endpoints ni modelos públicos.

También se evitó cambiar el comportamiento de RSS, alertas o worker salvo donde era necesario para mantener la integridad referencial.

## Integridad referencial

La integridad entre categorías y canales RSS queda protegida por dos lados:

- No se puede crear ni actualizar un canal RSS con una categoría inexistente, porque RSS sigue usando `ensure_category_exists`.
- No se puede borrar una categoría que tenga canales RSS activos asociados, porque `DELETE /categories/{category_id}` comprueba `rss_channels_col` y devuelve `409`.

Esto evita canales RSS huérfanos asociados a categorías inexistentes.

## Tests ejecutados

Se ejecutaron estos comandos:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_api_features.py backend/tests/test_seed_data.py
```

Resultado:

```text
14 passed
```

También se ejecutó compilación rápida:

```powershell
.\.venv\Scripts\python.exe -m py_compile backend/app/category/routes.py backend/app/app.py backend/app/rss/routes.py
```

Resultado: correcto, sin errores.

## Nota sobre `test_rss.py`

También se intentó ejecutar:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_api_features.py backend/tests/test_seed_data.py backend/tests/test_rss.py
```

Los tests unitarios nuevos y los de seed pasaron, pero `backend/tests/test_rss.py` falló en setup porque el entorno local no tenía MongoDB accesible en `mongodb:27017`.

El error fue de conexión a MongoDB (`ServerSelectionTimeoutError`), no una aserción fallida de la lógica modificada.

En CI o Docker, el flujo esperado del proyecto es ejecutar los tests con Mongo levantado, como indica `.github/workflows/main.yml`.

## Archivos modificados

- `backend/app/category/routes.py`
- `backend/app/app.py`
- `backend/tests/test_api_features.py`
- `docs/categorias-backend-crud.md`

