# Checklist de Verificación Funcional

Fecha: 2026-04-29

## Objetivo

Checklist de validación funcional final del sistema, siguiendo el estilo de la plantilla entregada en Aula Global.

## Estado

Leyenda:

- `SI`: comprobado y correcto
- `NO`: comprobado y no conforme
- `N/P`: no probado o no procede todavía

| ID | Pregunta / Check de comprobación | Referencia | SI | NO | N/P | Evidencia | Comentarios |
|---|---|---|---|---|---|---|---|
| F-01 | ¿Existe endpoint para listar el buzón interno de notificaciones del usuario? | `backend/app/notificaciones/routes.py`, `docs/workflow-alertas-notificaciones.md` | | | X | | Comprobar filtrado por `user_id` y canal `app` |
| F-02 | ¿Se puede obtener el detalle de una notificación del buzón del usuario? | `backend/app/notificaciones/routes.py`, `docs/contrato-api-backend.md` | | | X | | Verificar que no expone campos internos extra |
| F-03 | ¿Se puede marcar una notificación como leída y actualizar `read_at`? | `backend/app/notificaciones/routes.py`, `docs/workflow-alertas-notificaciones.md` | | | X | | Debe devolver la nueva fecha de lectura |
| F-04 | ¿El envío de correo usa configuración SMTP válida en el worker? | `shared/utils/email_sender.py`, `docker-compose.yml`, `.env.example` | | | X | | Comprobar `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` y `MAIL_FROM` |
| F-05 | ¿Las notificaciones pendientes pasan de `pending` a `sent` o `failed`? | `rss-worker/alerts/processor.py`, `rss-worker/alerts/notifications.py` | | | X | | Incluye reintento de outbox |
| F-06 | ¿El contrato API de alertas y notificaciones coincide con la documentación actual? | `docs/contrato-api-backend.md`, `docs/legacy/informe-conformidad-contrato-api-2026-04-15.md` | | | X | | Separar contracto base y extensiones |
| F-07 | ¿El alta de fuentes RSS funciona de extremo a extremo? | `frontend/src/pages/SourcesPage.jsx`, `backend/app/rss/routes.py` | | | X | | Preview, selección manual de categoría y alta final |
| F-08 | ¿El alta de un canal RSS queda vinculada a su fuente y categoría? | `backend/app/rss/routes.py`, `docs/api -añadir-fuentes-rss.md` | | | X | | Debe respetar la relación fuente-canal |
| F-09 | ¿MongoDB crea toda la estructura necesaria desde el bootstrap inicial? | `scripts/mongo/init-mongo.js`, `scripts/mongo/init-mongo.sh` | | | X | | Las colecciones no deben surgir en runtime |
| F-10 | ¿Backend y workers operan con el usuario de aplicación de MongoDB? | `shared/mongo/Database.py`, `docker-compose.yml`, `.env.example` | | | X | | Requisito posterior a cerrar el bootstrap |

## Notas

- Añadir una fila por cada requisito funcional o caso de prueba manual.
- Usar la columna `Referencia` para enlazar enunciado, adenda, ADR o contrato API.
- Usar la columna `Evidencia` para apuntar capturas, logs, commits o endpoints probados.
