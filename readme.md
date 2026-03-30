##  Estado del Proyecto (Sprint 1)

Actualmente, el proyecto cuenta con un sistema de **Integración Continua (CI)** mediante GitHub Actions que valida cada cambio en el código.

* **Estado actual:** 🟢 PASSING
* **Última ejecución:** Validada la conectividad de MongoDB, Backend y SMTP.

**Validaciones automatizadas:**
* **Despliegue:** Construcción de imágenes Docker y orquestación con Compose.
* **Backend:** Health check del servidor FastAPI (Python 3.14).
* **Database:** Test de conexión y autenticación con MongoDB 7.0.
* **Seguridad:** Verificación de aislamiento de variables de entorno.
* **Notificaciones:** Integración con servicio SMTP (Gmail).

> Para ejecutar los tests localmente: `docker exec -e MONGODB_URI="mongodb://newsradar_root:change_me_root_pwd@mongodb:27017/admin?authSource=admin" newsradar-backend pytest -s test/test_sprint1.py`

> **Nota:** Los logs detallados de la ejecución de las pruebas se encuentran en la pestaña **Actions** del repositorio (requiere acceso de colaborador).
