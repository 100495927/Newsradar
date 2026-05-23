# Checklist de Cierre de Entrega

Fecha: 2026-04-29

## Objetivo

Checklist operativo para revisar que la entrega final queda lista a nivel de repositorio, documentación, demo y despliegue.

## Estado

Leyenda:

- `SI`: completado
- `NO`: pendiente o incorrecto
- `N/P`: no aplica

| ID | Tarea de cierre | Referencia | SI | NO | N/P | Evidencia | Comentarios |
|---|---|---|---|---|---|---|---|
| C-01 | Verificar que el worker recibe variables SMTP y puede preparar el envío de correo | `shared/utils/email_sender.py`, `docker-compose.yml`, `.env.example` | | | X | | Primer paso antes de validar la entrega real |
| C-02 | Confirmar que el `alert-worker` dispone de `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` y `MAIL_FROM` | `docker-compose.yml`, `.env.example` | | | X | | Evita que el envío falle por configuración incompleta |
| C-03 | Añadir la vista o buzón de notificaciones en frontend y conectarla a la API | `backend/app/notificaciones/routes.py`, `frontend/src/App.jsx`, `frontend/src/components/SideNavBar.jsx`, `frontend/src/components/MobileNav.jsx` | | | X | | Debe permitir listar, leer y marcar notificaciones |
| C-04 | Documentar el workflow completo de alertas y notificaciones con los endpoints reales | `docs/workflow-alertas-notificaciones.md`, `docs/contrato-api-backend.md` | | | X | | Separar contrato público, extensiones y flujo interno |
| C-05 | Crear o cargar el inventario de 100 fuentes RSS iniciales | `docs/api -añadir-fuentes-rss.md`, `docs/rss_probe/rss_probe_summary.json` | | | X | | Primero se valida el inventario, luego el alta masiva |
| C-06 | Verificar que cada fuente inicial puede darse de alta como fuente y como canal RSS | `frontend/src/pages/SourcesPage.jsx`, `backend/app/rss/routes.py` | | | X | | Incluye preview, alta y borrado |
| C-07 | Eliminar la creación de colecciones desde runtime en backend y workers | `shared/mongo/Database.py`, `shared/mongo/colecciones/*`, `rss-worker/*` | | | X | | Todo debe depender del bootstrap de Mongo |
| C-08 | Dejar a backend y workers conectando solo con el usuario de aplicación de MongoDB | `shared/mongo/Database.py`, `docker-compose.yml`, `.env.example` | | | X | | Esto va después de cerrar la creación de colecciones |
| C-09 | Simplificar el modelo de datos para alertas, notificaciones y fuentes RSS | `scripts/mongo/init-mongo.js`, `docs/informe-sprint-2-base-datos-mongodb.md` | | | X | | Reducir campos redundantes y dependencias cruzadas |
| C-10 | Revisar y documentar las diferencias pendientes respecto al contrato API oficial | `docs/contrato-api-backend.md`, `docs/legacy/informe-conformidad-contrato-api-2026-04-15.md` | | | X | | Dejar claro qué es contrato y qué es extensión |

## Notas

- Usar este checklist para repasar entregables, documentación, entorno de demo y validaciones finales.
- Si una tarea depende de otra, reflejarlo en `Comentarios`.
