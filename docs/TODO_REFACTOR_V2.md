# TODO Refactorizacion `v2`

Documento de trabajo para alinear la refactorizacion de `newsradar-g5-2026 v2`.

## Objetivo

Dejar `v2` como la base estructural del proyecto, simplificando la arquitectura y manteniendo el entorno de desarrollo comodo para reinicios frecuentes de base de datos con bind mounts.

## Decisiones ya alineadas

- Se mantienen los bind mounts de `MongoDB` y `Elasticsearch` para poder inspeccionar datos desde VS Code y facilitar resets en desarrollo.
- Se quiere eliminar `mongo-handler` como servicio permanente.
- La inicializacion de Mongo debe hacerse desde `init-mongo.sh`.
- `v2` se toma como base de reestructuracion.

## Todo List

### 1. Docker e infraestructura

- [ ] Eliminar el servicio `mongo-handler` de `newsradar-g5-2026 v2/docker-compose.yml`.
- [ ] Hacer que `backend` y `rss-worker` dependan directamente de `mongodb`.
- [ ] Revisar y ajustar los healthchecks tras quitar `mongo-handler`.
- [ ] Mantener los bind mounts actuales de `data/mongodb` y `data/elasticsearch`.
- [ ] Valorar si `kibana` debe ir siempre activo o bajo `profiles`.

### 2. Bootstrap de MongoDB

- [ ] Ampliar `newsradar-g5-2026 v2/scripts/mongo/init-mongo.sh`.
- [ ] Crear desde el `init` el usuario de aplicacion.
- [ ] Crear desde el `init` las colecciones necesarias.
- [ ] Crear desde el `init` los validadores de esquema.
- [ ] Crear desde el `init` los indices necesarios.
- [ ] Hacer el `init` idempotente para que no falle si algo ya existe.
- [ ] Decidir si `rss_entradas_raw` sigue siendo parte del modelo o se elimina definitivamente.

### 3. Refactor de la capa Mongo en Python

- [ ] Convertir `shared/mongo/Database.py` en una capa solo de acceso runtime.
- [ ] Quitar del runtime la necesidad de credenciales root si dejan de ser necesarias.
- [ ] Quitar de `shared/mongo/colecciones/Coleccion.py` la responsabilidad de crear o modificar colecciones.
- [ ] Dejar en las clases de coleccion solo operaciones de negocio: insertar, listar, consultar.
- [ ] Revisar si `db_admin` y `login_como_admin()` deben desaparecer o quedar solo para migraciones futuras.

### 4. RSS Worker

- [ ] Refactorizar `newsradar-g5-2026 v2/rss-worker/worker/main.py`.
- [ ] Añadir manejo de errores por feed.
- [ ] Añadir manejo de errores por ciclo completo.
- [ ] Añadir logs claros con numero de fuentes, entradas y duracion.
- [ ] Evitar que una fuente RSS defectuosa tumbe el contenedor entero.
- [ ] Revisar si el worker debe seguir sembrando fuentes al arrancar o si eso pertenece a otro paso.
- [ ] Revisar `rss-worker/worker/test.py` para evitar falsos negativos en healthchecks.

### 5. Elasticsearch

- [ ] Decidir si la sincronizacion `Mongo -> Elasticsearch` es requisito actual.
- [ ] Si es requisito, reintroducirla de forma explicita y mantenible.
- [ ] Si no es requisito, limpiar variables, docs y expectativas para que el repo no sugiera una funcionalidad inexistente.

### 6. Variables de entorno

- [ ] Fijar un naming canonico para variables de Mongo.
- [ ] Mantener compatibilidad legacy solo si sigue siendo necesaria durante la transicion.
- [ ] Alinear `.env.example`, `docker-compose.yml` y `shared/mongo/EntornoDB.py`.
- [ ] Revisar nombres como `MONGO_EXPOSE_PORT` y `MONGO_EXPOSED_PORT` para evitar duplicidades innecesarias.

### 7. Build y estructura

- [ ] Crear un `.dockerignore` en la raiz del repo de `v2`.
- [ ] Evitar enviar al build context archivos pesados o irrelevantes como `docs`, `.git`, zips, excels y datos locales.
- [ ] Revisar `backend/Dockerfile` y `rss-worker/Dockerfile` para copiar solo lo necesario.
- [ ] Confirmar que `shared/` queda como unica libreria comun entre backend y worker.

### 8. Testing

- [ ] Mantener los smoke tests actuales.
- [ ] Añadir test de bootstrap de Mongo.
- [ ] Añadir test de integracion del worker en modo `run_once`.
- [ ] Añadir test de deduplicacion en `rss_entradas`.
- [ ] Si vuelve la indexacion a Elasticsearch, añadir test de indexacion.

### 9. Documentacion

- [ ] Actualizar `readme.md` de `v2` para reflejar la arquitectura final.
- [ ] Documentar que Mongo se inicializa desde `init-mongo.sh`.
- [ ] Documentar el uso esperado de bind mounts en desarrollo.
- [ ] Documentar el flujo de reset de datastores y rebootstrap.

## Orden recomendado de ejecucion

1. Quitar `mongo-handler`.
2. Pasar bootstrap completo a `init-mongo.sh`.
3. Limpiar `Database` y `Coleccion` para dejar solo runtime.
4. Endurecer el `rss-worker`.
5. Decidir y cerrar Elasticsearch.
6. Añadir tests.
7. Actualizar documentacion.

## Nota

`init-mongo.sh` es una buena solucion para bootstrap inicial porque este proyecto trabaja en entorno de desarrollo con resets frecuentes. Si en el futuro se necesitan cambios de esquema sobre bases ya inicializadas, convendra valorar un script de migracion separado.
