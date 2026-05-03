# ADR 012: Migración de endpoints custom de estadísticas al contrato oficial GET /api/v1/stats

* **Fecha:** 03/05/2026
* **Decisores:** Equipo NewsRadar (6 miembros)

## Contexto

El frontend consumía tres endpoints de estadísticas que no formaban parte del contrato oficial de la API definido en `api_ag_comentado.py`:

| Endpoint anterior (custom) | Propósito |
|---|---|
| `GET /api/v1/stats/global` | Contadores globales: nº fuentes, noticias, alertas, canales RSS y noticias por categoría |
| `GET /api/v1/stats/timeline` | Serie temporal de noticias procesadas por día (últimos 30 días) |
| `GET /api/v1/stats/cloud/{category}` | Frecuencia de palabras (nube) para una categoría IPTC concreta |

El contrato oficial únicamente expone un CRUD genérico en `/api/v1/stats` que devuelve objetos de la forma:

```json
{ "id": 1, "metrics": [{ "name": "string", "value": 0.0 }] }
```

Los tres endpoints custom no estaban documentados ni en el contrato OpenAPI ni en el enunciado. Su existencia creaba una dependencia implícita entre el frontend y una implementación de backend no verificable, lo que suponía un riesgo de rotura en el entorno de evaluación del profesor.

## Decisión

Reescribir `frontend/src/api/apiClient.js` para derivar todos los datos de visualización del endpoint estándar `GET /api/v1/stats`, acordando con el equipo de backend una **convención de nombres de métricas**:

| Nombre de métrica | Significado |
|---|---|
| `sources_count` | Nº total de fuentes de información |
| `news_count` | Nº total de noticias procesadas |
| `alerts_count` | Nº total de alertas registradas |
| `rss_channels_count` | Nº total de canales RSS |
| `news_cat_<code>` | Noticias de la categoría IPTC `<code>` (ej. `news_cat_01000000`) |
| `timeline_<YYYY-MM-DD>` | Noticias procesadas en esa fecha (ej. `timeline_2026-04-01`) |
| `cloud_<code>_<palabra>` | Frecuencia de `<palabra>` en categoría `<code>` (ej. `cloud_01000000_elecciones`) |

El frontend usa el objeto `Stats` con el `id` más alto (el más reciente). Las funciones `getGlobalStats()`, `getTimeline()` y `getWordCloud()` mantienen exactamente la misma firma de retorno que antes, de modo que `DashboardPage` y `SummaryPage` no requieren ningún cambio.

Se añade una caché interna de 30 segundos para evitar llamadas duplicadas a `/api/v1/stats` cuando varias funciones se invocan en el mismo ciclo de render.

## Motivo

1. **Conformidad con el contrato:** El enunciado indica que la verificación funcional del sistema se realizará a través del API REST documentada con OpenAPI (Anexo I). Usar endpoints fuera de ese contrato hace que el sistema falle si el backend evaluado solo implementa el contrato estándar.
2. **Desacoplamiento:** Con la convención de nombres, el backend puede poblar el objeto `Stats` de la manera que considere oportuna (cron periódico, tras cada indexación, etc.) sin que el frontend deba conocer la lógica interna.
3. **Sin rotura de interfaz:** Las páginas `DashboardPage` y `SummaryPage` no se modificaron — solo cambió la capa de acceso a datos.

## Consecuencias

* El backend **debe** crear al menos un objeto `Stats` con las métricas descritas en la convención anterior para que el dashboard y la página de resumen muestren datos.
* Si el objeto `Stats` está vacío o no existe, las páginas muestran ceros y la nube de palabras aparece vacía (comportamiento gracioso, sin error de consola).
* Los tres endpoints custom (`/stats/global`, `/stats/timeline`, `/stats/cloud/*`) pueden eliminarse del backend si no tienen otro consumidor.
