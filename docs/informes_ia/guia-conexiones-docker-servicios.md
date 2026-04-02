# Guia de conexiones Docker y servicios - NewsRadar

Fecha: 31/03/2026

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
- frontend
  - Contenedor: newsradar-frontend
  - Puerto contenedor: 5173
  - Puerto host: ${FRONTEND_EXPOSE_PORT:-5173}
  - URL local: [http://localhost:5173](http://localhost:5173)
- elasticsearch
  - Contenedor: newsradar-elasticsearch
  - Puerto contenedor: 9200
  - Puerto host: ${ELASTIC_EXPOSE_PORT:-9200}
  - URL local: [http://localhost:9200](http://localhost:9200)
- kibana
  - Contenedor: newsradar-kibana
  - Puerto contenedor: 5601
  - Puerto host: ${KIBANA_EXPOSE_PORT:-5601}
  - URL local: [http://localhost:5601](http://localhost:5601)

## 2. Archivo .env para el equipo

Referencia base en [.env.example](.env.example).

Para este proyecto educativo, se trabaja con un `.env` operativo compartido por el equipo.

Flujo acordado:

1. Recibir el archivo `.env` por WhatsApp (responsable del equipo).
2. Guardarlo en la raiz del repositorio con nombre exacto `.env`.
3. Verificar que contiene variables de backend, MongoDB, frontend, Elasticsearch, Kibana y SMTP.
4. No hace falta instalar nada adicional: Docker Compose lo carga automaticamente al ejecutar comandos desde la raiz.

Si alguien no recibe el `.env`, puede crearlo copiando `.env.example` y ajustando solo lo necesario para su entorno local.

## 3. Comandos de arranque recomendados

Desde la raiz del repo:

1. Arrancar servicios (backend, frontend, MongoDB, Elasticsearch y Kibana):

```powershell
docker compose up -d --build
```

1. Ver estado:

```powershell
docker compose ps
```

1. Ver logs de un servicio:

```powershell
docker logs -f newsradar-mongodb
docker logs -f newsradar-backend
docker logs -f newsradar-elasticsearch
docker logs -f newsradar-kibana
docker logs -f newsradar-frontend
```

## 4. Puntos de acceso y verificacion rapida

- Backend health: [http://localhost:8000/health](http://localhost:8000/health)
- Frontend: [http://localhost:5173](http://localhost:5173)
- Elasticsearch health:

```powershell
Invoke-RestMethod http://localhost:9200/_cluster/health
```

- Kibana status:

```powershell
Invoke-WebRequest http://localhost:5601/api/status
```

## 5. Metodos de conexion a MongoDB

### Metodo A: desde host con URI de aplicacion

```text
mongodb://newsradar_app:<MONGO_APP_PASSWORD>@localhost:27017/newsradar?authSource=admin
```

### Metodo B: desde host con usuario root

```text
mongodb://newsradar_root:<MONGO_ROOT_PASSWORD>@localhost:27017/admin
```

### Metodo C: desde el contenedor backend (red interna docker)

```text
mongodb://newsradar_app:<MONGO_APP_PASSWORD>@mongodb:27017/newsradar?authSource=admin
```

### Metodo D: shell interactiva dentro del contenedor Mongo

```powershell
docker exec -it newsradar-mongodb mongosh
```

## 6. Metodos de conexion a Elasticsearch

### Metodo A: desde host

```text
http://localhost:9200
```

### Metodo B: desde contenedores en red Docker

```text
http://elasticsearch:9200
```

### Metodo C: prueba de conectividad

```powershell
Invoke-RestMethod http://localhost:9200
Invoke-RestMethod http://localhost:9200/_cat/indices?v
```

## 7. Metodos de acceso a Kibana

### Metodo A: navegador local

Abrir [http://localhost:5601](http://localhost:5601).

### Metodo B: status API

```powershell
Invoke-WebRequest http://localhost:5601/api/status
```

Kibana esta configurado para conectarse a Elasticsearch por red interna con `http://elasticsearch:9200`.

## 8. Persistencia y reinicio de datos

Persistencia declarada en carpetas del proyecto (bind mounts):

- MongoDB datos: `./data/mongodb/data`
- MongoDB configdb: `./data/mongodb/configdb`
- Elasticsearch datos: `./data/elasticsearch/data`
- Elasticsearch config: `./data/elasticsearch/config/elasticsearch.yml`

Si se necesita resetear datos en local (destructivo):

```powershell
docker compose down
Remove-Item -Recurse -Force .\data\mongodb\data\*
Remove-Item -Recurse -Force .\data\mongodb\configdb\*
Remove-Item -Recurse -Force .\data\elasticsearch\data\*
docker compose up -d --build
```

## 9. Troubleshooting rapido

1. Si Kibana no levanta, comprobar primero Elasticsearch:

```powershell
docker logs newsradar-elasticsearch
Invoke-RestMethod http://localhost:9200/_cluster/health
```

1. Si el backend no conecta con Mongo, revisar URI y credenciales del `.env` y reiniciar:

```powershell
docker compose up -d --build backend mongodb
```

1. Si hay cambios en variables y no se reflejan, recrear contenedores:

```powershell
docker compose down
docker compose up -d --build
```
