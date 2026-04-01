# Informe Sprint 2 - Base de Datos MongoDB y Analisis RSS - NewsRadar

Fecha: 25/03/2026

## Objetivo de esta iteracion
Iniciar la implementacion tecnica priorizando:
1. Investigacion de formatos RSS reales (muestreo automatizado).
2. Preparacion de MongoDB para persistencia de noticias y usuarios.
3. Preparacion de persistencia para JWT futuro sin implementar backend de autenticacion hoy.

## Alcance acordado
- SI entra en alcance hoy:
  - Script de muestreo RSS y analisis estructural.
  - Creacion de colecciones e indices MongoDB para noticias, fuentes, usuarios y sesiones JWT futuras.
- NO entra en alcance hoy:
  - Endpoints de autenticacion (register/login/refresh/logout).
  - Emision y validacion de tokens JWT en backend.

## Implementacion realizada

### 1) Script de muestreo RSS multi-fuente
Se implemento el script [backend/scripts/rss_format_sampler.py](backend/scripts/rss_format_sampler.py).

Capacidades:
- Consulta feeds RSS reales de multiples fuentes (incluye CNMV, Una al Dia, BBC, DSCA, La Moncloa, RTVE).
- Guarda XML bruto por fuente en [docs/rss_probe/raw](docs/rss_probe/raw).
- Genera resumen estructurado JSON en [docs/rss_probe/rss_probe_summary.json](docs/rss_probe/rss_probe_summary.json).
- Genera matriz Markdown de comparacion en [docs/rss_probe/rss_probe_matrix.md](docs/rss_probe/rss_probe_matrix.md).
- Reporta cobertura de campos clave por feed (`title`, `link`, `summary`, `content`, `published`, `authors`, `tags`).
- Detecta namespaces y registra el primer `pubDate` observado.

Comando de ejecucion utilizado:
```powershell
& "d:/UC3M/5º Curso/2º Cuatrimestre/Devops/newsradar-g5-2026/.venv/Scripts/python.exe" backend/scripts/rss_format_sampler.py
```

Resultado de ejecucion:
- Feeds procesados: 7
- Correctos: 7
- Errores: 0

### 2) Inicializacion MongoDB con colecciones e indices
Se actualizo [docker/mongo/init-mongo.sh](docker/mongo/init-mongo.sh).

Nuevas colecciones definidas:
- `rss_sources`
- `rss_items`
- `rss_items_raw`
- `users`
- `user_sessions` (soporte futuro JWT)

Nuevos elementos tecnicos:
- Validaciones JSON Schema por coleccion (`validationLevel: moderate`).
- Indices de deduplicacion y consulta temporal para RSS.
- Indice unico de email en usuarios.
- Indices de sesiones por `jti`, `user_id`, `token_type`, `status`.
- TTL index en `user_sessions.expires_at` para limpieza automatica de sesiones/tokens expirados.

## Hallazgos rapidos de formatos RSS (evidencia inicial)
Basado en [docs/rss_probe/rss_probe_matrix.md](docs/rss_probe/rss_probe_matrix.md):
- Todos los feeds muestreados usan `rss20`, pero con variaciones de namespaces.
- `una_al_dia` presenta estructura mas rica (`content`, `authors`, `tags`).
- `dsca_noticias` usa fecha no RFC clasica en `pubDate` (ejemplo: "22 de Marzo de 2026").
- CNMV y otros feeds institucionales mantienen estructura mas simple y estable.

Implicacion para modelo de datos:
- Se confirma necesidad de documento canonicamente normalizado + almacenamiento raw por heterogeneidad.
- Se confirma necesidad de campos opcionales y trazabilidad de parseo por fuente.

## Estado frontend y auth (sin implementacion en esta iteracion)
- Frontend mantiene pantallas de login/registro/perfil.
- No se ha implementado backend auth en esta iteracion por decision de alcance.
- La coleccion `user_sessions` se deja preparada para JWT futuro sin bloquear trabajo posterior.

## Riesgos y notas
1. CNMC puede requerir estrategia adicional de extraccion por restricciones de acceso web.
2. El parser actual puede requerir endurecimiento en fechas no estandar y campos opcionales.
3. Es recomendable rotar credenciales reales si aparecen en archivos de ejemplo antes de cualquier despliegue compartido.

## Proximos pasos sugeridos
1. Extender muestreo a mas feeds (>=10) y cerrar matriz de generalizacion XML.
2. Crear script de seeding inicial para `rss_sources` desde listado estandar del proyecto.
3. Integrar persistencia real `rss_items`/`rss_items_raw` desde pipeline de parseo existente.
4. Definir DTO canonico final para ingesta y consumo frontend.
5. En una siguiente iteracion, implementar backend auth usando JWT sobre la base ya preparada.

## Actualizacion 26/03/2026

### A) Frontend Docker alineado con comando start
Se actualizo la ejecucion del frontend para usar `npm run start`:
- [frontend/package.json](frontend/package.json): se anadio script `start` con Vite en `0.0.0.0:5173`.
- [frontend/Dockerfile](frontend/Dockerfile): ahora arranca con `CMD ["npm", "run", "start"]`.

### B) Renombrado del informe
Este documento reemplaza al antiguo nombre de informe del Sprint 2 para reflejar explicitamente Sprint + Base de Datos, evitando la palabra "estado".

### C) Guia de conexiones Docker y servicios
Se creo la guia operativa [docs/informes_ia/guia-conexiones-docker-servicios.md](docs/informes_ia/guia-conexiones-docker-servicios.md) con:
- Puertos y servicios.
- Comandos de arranque.
- Metodos de conexion a Mongo (host, contenedor, URI de app y root).
- Recomendaciones de configuracion base para siguiente sprint backend.
