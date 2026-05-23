# Verificación Docker y MongoDB del CRUD de categorías

Fecha de verificación: 2026-05-06

## Objetivo

Validar en un entorno real con Docker y MongoDB levantados que los cambios recientes en la gestión de categorías funcionan correctamente.

La verificación se centró especialmente en:

- Carga inicial de categorías.
- Creación real de categorías.
- Rechazo de duplicados por nombre normalizado.
- Actualización persistente de categorías.
- Borrado de categorías.
- Bloqueo de borrado si hay canales RSS activos asociados.
- Validación de `category_id` al crear o actualizar canales RSS.
- Ausencia de canales RSS huérfanos tras las operaciones.

## Estado del stack Docker

Al inicio, `docker compose ps` no mostraba servicios activos para este proyecto, así que se levantó el stack con:

```powershell
docker compose up -d --build
```

Después del arranque, los servicios quedaron en estado healthy:

```text
newsradar-mongodb      healthy
newsradar-rss-worker   healthy
newsradar-backend      healthy
newsradar-frontend     healthy
newsradar-alert-worker healthy
```

El backend quedó disponible en:

```text
http://localhost:8000
```

MongoDB quedó disponible en:

```text
localhost:27017
```

## Tests focalizados ejecutados

Se ejecutaron dentro del contenedor backend los tests directamente relacionados con categorías, seed data y RSS:

```powershell
docker exec -e PYTHONPATH="/app:/app/backend" newsradar-backend pytest tests/test_api_features.py tests/test_seed_data.py tests/test_rss.py
```

Resultado:

```text
16 passed
```

Estos tests cubren:

- `GET /categories` con catálogo inicial.
- `POST /categories` creando categoría real.
- Rechazo de duplicados por nombre normalizado.
- `PUT /categories/{id}` persistiendo cambios.
- `PUT /categories/{id}` con categoría inexistente.
- `DELETE /categories/{id}` con y sin canales RSS asociados.
- Creación de RSS con categoría inexistente.
- Actualización de RSS hacia categoría inexistente.
- Flujo RSS completo con Mongo real.

## Suite completa del backend

También se ejecutó la suite completa del backend, igual que en CI:

```powershell
docker exec -e PYTHONPATH="/app:/app/backend" newsradar-backend pytest tests/
```

Resultado:

```text
43 passed
```

Esto confirma que los cambios de categorías no rompieron otras áreas del backend como autenticación, alertas, notificaciones, roles, bootstrap Mongo, RSS, seed data o estadísticas.

## Prueba funcional por HTTP

Además de los tests automatizados, se hizo una prueba funcional contra la API HTTP real del contenedor backend.

El flujo probado fue:

1. Registrar usuario temporal.
2. Hacer login.
3. Obtener categorías iniciales.
4. Crear una categoría nueva.
5. Confirmar que el ID creado no es `-1`.
6. Intentar crear duplicado con nombre normalizado equivalente.
7. Actualizar la categoría.
8. Intentar actualizar una categoría inexistente.
9. Crear una fuente de información.
10. Intentar crear un canal RSS con categoría inexistente.
11. Crear un canal RSS con la categoría creada.
12. Intentar borrar la categoría mientras tiene un canal RSS activo.
13. Intentar actualizar el canal RSS hacia una categoría inexistente.
14. Borrar el canal RSS.
15. Borrar la categoría ya sin canales activos.
16. Confirmar que la categoría borrada devuelve `404`.

Resultado de la prueba HTTP:

```text
register test user                              201 OK
login test user                                 200 OK
GET categories initial catalog                  200 OK
initial catalog is not empty                    count=17 OK
POST category creates real category             201 OK
created category id is real                     id=1 OK
POST category rejects normalized duplicate      409 OK
PUT category updates existing category          200 OK
updated category name persisted in response     OK
PUT category missing returns 404                404 OK
POST information source                         201 OK
POST RSS channel rejects missing category       404 OK
POST RSS channel accepts existing category      201 OK
DELETE category with active RSS returns 409     409 OK
PUT RSS channel rejects missing category        404 OK
DELETE RSS channel cleanup                      204 OK
DELETE category without active RSS succeeds     204 OK
GET deleted category returns 404                404 OK
```

## Comprobación de limpieza en MongoDB

Después de la prueba HTTP se comprobó que no quedaran datos temporales activos o categorías de prueba:

```text
qa_categories_remaining: 0
qa_users_remaining: 0
active_qa_sources_remaining: 0
active_qa_channels_remaining: 0
```

Esto confirma que la prueba no dejó categorías temporales, usuarios temporales ni canales RSS activos de prueba.

## Conclusión

La parte modificada funciona correctamente en Docker con MongoDB real.

Queda validado que:

- Las categorías iniciales siguen cargándose.
- `POST /categories` crea y persiste categorías reales.
- Ya no se devuelve `id=-1`.
- Se rechazan duplicados por nombre normalizado.
- `PUT /categories/{id}` actualiza y persiste.
- `PUT /categories/{id}` devuelve `404` si la categoría no existe.
- `DELETE /categories/{id}` devuelve `409` si hay canales RSS activos asociados.
- `DELETE /categories/{id}` elimina la categoría si no hay canales asociados.
- RSS no permite crear canales con categoría inexistente.
- RSS no permite actualizar canales hacia categoría inexistente.
- No se generan canales RSS huérfanos.
- La suite completa del backend pasa correctamente.

