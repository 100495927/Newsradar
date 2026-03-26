# Guia de conexiones Docker y MongoDB - NewsRadar

Fecha: 26/03/2026

## 1. Servicios Docker y puertos

Definidos en [docker-compose.yml](docker-compose.yml):

- mongodb
  - Contenedor: newsradar-mongodb
  - Puerto contenedor: 27017
  - Puerto host: ${MONGO_EXPOSE_PORT:-27017}
- backend
  - Contenedor: newsradar-backend
  - Puerto contenedor: 8000
  - Puerto host: ${BACKEND_EXPOSE_PORT:-8000}
  - Health endpoint: [http://localhost:8000/health](http://localhost:8000/health)
- frontend (perfil opcional frontend)
  - Contenedor: newsradar-frontend
  - Puerto contenedor: 5173
  - Puerto host: ${FRONTEND_EXPOSE_PORT:-5173}
  - URL local: [http://localhost:5173](http://localhost:5173)

## 2. Comandos de arranque recomendados

Desde la raiz del repo:

1. Arrancar backend + mongo:

```powershell
docker compose up -d --build
```

1. Arrancar tambien frontend (perfil opcional):

```powershell
docker compose --profile frontend up -d --build
```

1. Ver estado:

```powershell
docker compose ps
```

1. Ver logs de un servicio:

```powershell
docker logs -f newsradar-mongodb
docker logs -f newsradar-backend
docker logs -f newsradar-frontend
```

## 3. Frontend en Docker

Configuracion actual:

- [frontend/package.json](frontend/package.json): script start disponible.
- [frontend/Dockerfile](frontend/Dockerfile): arranque con npm run start.

Si se desea ejecutar frontend fuera de Docker:

```powershell
cd frontend
npm install
npm run start
```

## 4. Variables de entorno clave

Referencia base en [.env.example](.env.example).

Variables de Mongo:

- MONGO_ROOT_USERNAME
- MONGO_ROOT_PASSWORD
- MONGO_INITDB_DATABASE (default admin)
- MONGO_APP_USER
- MONGO_APP_PASSWORD
- MONGO_APP_DB (default newsradar)
- MONGO_EXPOSE_PORT

Variables backend relacionadas:

- MONGODB_URI (se construye en compose para usuario app)
- MONGO_DB_NAME

Nota: crear un archivo .env local para sobreescribir credenciales y no usar valores por defecto.

## 5. Metodos de conexion a MongoDB

### Metodo A: desde host con URI de aplicacion

Uso recomendado para backend:

```text
mongodb://newsradar_app:<MONGO_APP_PASSWORD>@localhost:27017/newsradar?authSource=admin
```

### Metodo B: desde host con usuario root

Uso administrativo:

```text
mongodb://newsradar_root:<MONGO_ROOT_PASSWORD>@localhost:27017/admin
```

### Metodo C: desde el contenedor backend (red interna docker)

Host interno: mongodb

```text
mongodb://newsradar_app:<MONGO_APP_PASSWORD>@mongodb:27017/newsradar?authSource=admin
```

### Metodo D: shell interactiva dentro del contenedor Mongo

```powershell
docker exec -it newsradar-mongodb mongosh
```

Luego autenticar en admin y cambiar a DB de app:

```javascript
use admin
db.auth("newsradar_root", "<MONGO_ROOT_PASSWORD>")
use newsradar
```

### Metodo E: comprobacion rapida desde host

```powershell
docker exec newsradar-mongodb mongosh "mongodb://newsradar_app:<MONGO_APP_PASSWORD>@localhost:27017/newsradar?authSource=admin" --eval "db.runCommand({ ping: 1 })"
```

## 6. Configuracion MongoDB basica disponible hoy

La inicializacion en [docker/mongo/init-mongo.sh](docker/mongo/init-mongo.sh) deja:

Colecciones:

- rss_sources
- rss_items
- rss_items_raw
- users
- user_sessions (persistencia preparada para JWT futuro)

Indices destacados:

- Unicos: rss_sources.url, rss_items.dedup_key, users.email, user_sessions.jti
- Consulta: rss_items por source_id/published_at, users por role/status
- TTL: user_sessions.expires_at

Esto permite iniciar en el siguiente sprint la implementacion de backend con base de datos ya estructurada.

## 7. Verificaciones utiles

1. Listar colecciones:

```powershell
docker exec newsradar-mongodb mongosh "mongodb://newsradar_app:<MONGO_APP_PASSWORD>@localhost:27017/newsradar?authSource=admin" --eval "db.getCollectionNames()"
```

1. Ver indices de una coleccion:

```powershell
docker exec newsradar-mongodb mongosh "mongodb://newsradar_app:<MONGO_APP_PASSWORD>@localhost:27017/newsradar?authSource=admin" --eval "db.users.getIndexes()"
```

1. Probar backend health:

- [http://localhost:8000/health](http://localhost:8000/health)

1. Probar frontend (si perfil activado):

- [http://localhost:5173](http://localhost:5173)

## 8. Si no aparecen las nuevas colecciones

El script de init se ejecuta al inicializar el volumen de Mongo por primera vez.
Si el volumen ya existia, puede que no reaplique automaticamente.

Opciones:

1. Aplicar manualmente los comandos de colecciones/indices desde mongosh.
2. Re-crear solo el volumen de Mongo en entorno local de desarrollo (destructivo para datos actuales).

Comando destructivo solo en local:

```powershell
docker compose down
docker volume rm newsradar_mongodb_data
docker compose up -d --build
```
