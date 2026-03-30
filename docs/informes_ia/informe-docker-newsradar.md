# Informe de infraestructura Docker - NewsRadar

Fecha: 19/03/2026

## Objetivo
Preparar una infraestructura Docker lista para desplegar el backend de NewsRadar en Python (base Debian slim) con persistencia en MongoDB, y dejar preparada la estructura para alojar un frontend React con Node.js sin ejecutarlo por defecto.

## Decisiones alineadas con ADR
- ADR-001: backend en Python 3.12 slim.
- ADR-002: MongoDB como base de datos principal y volumen persistente.
- ADR-003: base de backend preparada para FastAPI.
- ADR-004: estructura de frontend React preparada con Node.js.

## Estructura creada
- docker-compose.yml
- .env.example
- backend/
  - Dockerfile
  - requirements.txt
  - app/main.py
- docker/mongo/
  - init-mongo.sh
- frontend/
  - Dockerfile
  - package.json
  - vite.config.js
  - index.html
  - .dockerignore
  - src/main.jsx
  - src/App.jsx

## Descripción de lo desarrollado
1. Se creó un servicio backend con imagen construida desde Dockerfile basado en python:3.12-slim-bookworm.
2. Se añadió servicio MongoDB con imagen oficial mongo:7.0.
3. Se configuró volumen persistente mongodb_data para conservar datos entre reinicios.
4. Se implementó script de inicialización init-mongo.sh para crear usuario de aplicación con rol readWrite.
5. Se añadieron healthchecks para backend y MongoDB.
6. Se configuró dependencia por estado saludable: backend espera a MongoDB.
7. Se incorporó un servicio frontend React (Node.js) en perfil opcional frontend para no arrancar por defecto.

## Variables de entorno y configuración
Todas las variables se declaran en .env.example para revisión:

### Backend
- APP_ENV=production
- APP_HOST=0.0.0.0
- APP_PORT=8000
- BACKEND_EXPOSE_PORT=8000
- LOG_LEVEL=info

### MongoDB root
- MONGO_ROOT_USERNAME=newsradar_root
- MONGO_ROOT_PASSWORD=change_me_root_pwd
- MONGO_INITDB_DATABASE=admin

### MongoDB app
- MONGO_APP_USER=newsradar_app
- MONGO_APP_PASSWORD=change_me_app_pwd
- MONGO_APP_DB=newsradar
- MONGO_EXPOSE_PORT=27017

### Frontend React (opcional)
- FRONTEND_NODE_ENV=development
- FRONTEND_PORT=5173
- FRONTEND_EXPOSE_PORT=5173
- VITE_API_BASE_URL=http://localhost:8000

## Sobre Nginx en este proyecto
Nginx no es obligatorio para la fase actual (backend + Mongo en entorno de desarrollo). En este momento puede considerarse sobreingeniería.

Sí aportaría valor cuando:
- se despliegue frontend estático en producción;
- se quiera terminación TLS y reverse proxy unificado;
- se necesite rate-limiting, cabeceras de seguridad y caché.

Conclusión práctica: por ahora es opcional y prescindible; recomendable en fase de producción pública.

## Pasos para completar la configuración
1. Copiar .env.example a .env y sustituir contraseñas por valores seguros.
2. Implementar en el backend la conexión real a MongoDB usando MONGODB_URI.
3. Añadir routers y modelos FastAPI del dominio (usuarios, noticias, alertas).
4. Arrancar backend + MongoDB:
   - docker compose up -d --build
5. Verificar estado:
   - docker compose ps
   - backend health: http://localhost:8000/health
6. Cuando se quiera probar frontend, arrancar también su perfil:
   - docker compose --profile frontend up -d --build
7. En producción, cerrar el puerto publicado de MongoDB y mantener acceso solo por red interna Docker.

## Observaciones
- Se intentó leer el PDF del proyecto, pero en este entorno no hay herramientas de extracción de texto instaladas para parsearlo correctamente.
- La configuración final sí respeta las decisiones explícitas de los ADR disponibles.
