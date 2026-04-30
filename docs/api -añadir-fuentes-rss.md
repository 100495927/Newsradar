## 🚀 API de Fuentes RSS

La API permite registrar nuevas fuentes de noticias (medios) en la base de datos para que el worker comience a procesar sus feeds automáticamente.

### Configuración del Servidor
El servidor corre bajo **FastAPI** y se levanta en un hilo independiente al iniciar el worker principal.
* **Host:** `0.0.0.0`
* **Puerto interno:** Definido por la variable de entorno `RSS_WORKER_UVICORN_PORT`. Por defecto escucha en el `8000` dentro del contenedor.
* **Puerto expuesto:** Definido por la variable de entorno `RSS_WORKER_UVICORN_EXPOSE_PORT`. Por defecto se publica en el `12670` del host.

---

### 1. Añadir/Actualizar Fuente
Registra un nuevo origen RSS en la colección de fuentes.

* **URL:** `/fuentes`
* **Método:** `POST`
* **Cuerpo (JSON):**

| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `medio` | String | Sí | Nombre del medio de comunicación. |
| `rss` | String | Sí | URL directa del feed RSS/XML. |
| `url` | String | Sí | URL del sitio web principal del medio. |
| `activo` | Boolean | Sí | Define si el worker debe procesar esta fuente. |
| `categoria_iptc` | String | No | Código de categoría estandarizada IPTC. |

#### Ejemplo de Petición
```json
{
    "medio": "El Mundo",
    "rss": "https://www.elmundo.es/rss/portada.xml",
    "url": "https://www.elmundo.es",
    "activo": true,
    "categoria_iptc": "04000000"
}
```

#### Respuestas
* **200 OK:** La fuente se ha insertado correctamente.
    ```json
    { "message": "Fuente insertada" }
    ```
* **Error:** Devuelve el mensaje de la excepción capturada.
    ```json
    { "message": "Error description..." }
    ```

---

## 🛠️ Detalles de Implementación

### Estructura de Datos (Pydantic)
La API utiliza el modelo `FuenteJSON` para validar los datos de entrada antes de transformarlos al objeto de dominio `RSSFuente`.

### Integración con el Worker
1.  **Hilo secundario:** La función `api_task` ejecuta `uvicorn` de forma asíncrona mediante `threading.Thread(daemon=True)`.
2.  **Persistencia:** Utiliza la conexión global de `Database()` para insertar los registros directamente en la colección `col_rss_fuentes`.

### Variables de Entorno Requeridas
Para que la API funcione, el archivo `Entorno.py` debe poder leer:
* `RSS_WORKER_UVICORN_PORT`: El puerto donde escuchará la API dentro del contenedor.
* `RSS_WORKER_UVICORN_EXPOSE_PORT`: El puerto del host que Docker mapeará hacia la API del worker.

---

## 🔍 Prueba de Salud (Healthcheck)
El archivo `test.py` incluye una función `test_uvicorn()` que verifica la disponibilidad de este endpoint realizando un `POST` de prueba a `http://localhost:{puerto}/fuentes` con un medio de test.
