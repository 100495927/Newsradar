## 🟢 Estado del Proyecto (Sprint 2)
**Estado de la CI:** ![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
**Arquitectura:** Sistema distribuido de 7 servicios orquestados con Docker.

### Validaciones Automatizadas en CI
En este Sprint hemos consolidado la integración de los siguientes componentes:
* **Motor de Búsqueda:** Health check de **Elasticsearch 9.3.2** y autoconfiguración de índices mediante *setup-worker*.
* **Persistencia:** Base de datos **MongoDB 8.2** con autenticación y volúmenes persistentes.
* **Backend:** Tests de integración con **Pytest** (validación de lógica de negocio y conectividad).
* **Notificaciones:** Flujo SMTP verificado mediante *Gmail App Passwords*.
* **Seguridad:** Verificación de aislamiento de variables de entorno (bloqueo de archivos `.env`).

## Guía de Ejecución y Tests

### 1. Levantar el entorno completo
Para arrancar todos los servicios (Frontend, Backend, Worker, Mongo, Elastic, Kibana):

`docker compose up -d --build`

## Guia de conexiones Docker

La documentacion operativa de servicios y accesos (MongoDB, Elasticsearch y Kibana) esta en:

- `docs/informes_ia/guia-conexiones-docker-servicios.md`

> **Nota:** Los logs detallados de la ejecución de las pruebas se encuentran en la pestaña **Actions** del repositorio (requiere acceso de colaborador).

### 2. Ejecutar tests de integración

Este es el comando que garantiza que el contrato entre servicios se cumple

`docker exec newsradar-backend pytest -s test/test_sprint1.py`

### 3. Scripts de pruebas manuales (Utilidades de equipo)

Si se necesita probar funcionalidades específicas de extracción o de persistencia:

  * **Poblar la base de datos con noticias reales:** `docker exec newsradar-backend python test/test_mongo_rss.py`

  * **Ver lectura de feeds por consola (Debug):** `docker exec newsradar-backend python test/test_rss.py`

## Accesos Directos (Entorno Local)

| Servicio | URL / Acceso |
| :--- | :--- |
| **Frontend (React)** | [http://localhost:5173](http://localhost:5173) |
| **API Backend (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Kibana (Dashboard BI)** | [http://localhost:5601](http://localhost:5601) |
| **Elasticsearch API** | [http://localhost:9200](http://localhost:9200) |

## Información del Sprint 1

<details>
<summary><b>Haz clic para ver los detalles del Sprint 1</b></summary>

### Logros alcanzados:
* **Conectividad:** Validación inicial de MongoDB, Backend y SMTP.
* **Despliegue:** Construcción de imágenes Docker y orquestación base.
* **Backend:** Health check inicial del servidor FastAPI.
* **Database:** Test de conexión y autenticación con MongoDB 7.0 (Migrado a 8.2 en Sprint 2).
* **Notificaciones:** Integración básica con servicio SMTP.

**Nota:** Los logs detallados de la ejecución de las pruebas se encuentran en la pestaña *Actions* del repositorio.

</details>

