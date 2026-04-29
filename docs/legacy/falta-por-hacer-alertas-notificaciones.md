# Alertas y Notificaciones: faltas por hacer

Este documento resume el estado real de la parte de alertas y notificaciones, separando lo que ya está implementado, lo que sigue incompleto, qué depende del resto de la API y qué se puede avanzar ya sin esperar a otras piezas.

## Ya está implementado

- Alta, listado, edición y borrado de alertas a través de la API modular.
- Alta, listado, edición y borrado de notificaciones a través de la API modular.
- El worker RSS ya genera matches cuando una entrada coincide con los descriptores de una alerta.
- El primer ciclo de una alerta nueva usa `created_at` como corte temporal, por lo que no hace match con noticias anteriores a la creación.
- El worker actualiza `last_checked_at` y `last_run_at` al terminar cada ciclo.

## Sigue incompleto

- `cron_expression` está guardado en la alerta, pero no se usa para decidir cuándo debe ejecutarse cada una.
- `next_run_at` existe en el esquema, pero todavía no se calcula ni se respeta.
- La creación de alertas fija `category_id` a `0` y deja `rss_channel_ids` vacío, así que la selección real de categoría y canales todavía no está conectada.
- La API pública de notificaciones expone una vista reducida y no devuelve todo el contenido interno que el worker ya guarda.
- El envío real de correo no está implementado; ahora mismo solo se marca `pending` o `skipped`.
- Las reglas de permisos para editar o borrar alertas no están cerradas del todo con lógica explícita de ownership y rol en todos los casos.

## Depende del resto de la API

- La validación de categorías depende de los endpoints y colecciones de categorías.
- La validación de fuentes y canales RSS depende de los endpoints y colecciones de RSS.
- La decisión final sobre el alcance de gestor y lector afecta a qué usuario puede crear, ver o modificar alertas ajenas.
- La exposición pública de notificaciones depende de cómo se quiera mostrar `subject`, `matches`, `delivery_channels`, `email_status` y `read_at`.

## Se puede implementar ya

- Usar `cron_expression` para calcular `next_run_at` y saltar alertas que aún no tocan.
- Endurecer permisos de actualización y borrado de alertas con rol y propiedad del recurso.
- Ampliar el modelo público de notificaciones para devolver `subject`, `matches`, `delivery_channels`, `email_status` y `read_at`.
- Añadir un endpoint para marcar notificaciones como leídas usando el campo `read_at`.
- Validar el formato de `cron_expression` al crear o editar alertas.
- Crear un worker o tarea de entrega de correo que pase las notificaciones de `pending` a `sent` o `failed`.

## Prioridad sugerida

1. Permisos y seguridad de alertas.
2. Uso real de `cron_expression` y `next_run_at`.
3. Ampliación de la respuesta pública de notificaciones.
4. Envío de correo asíncrono.
5. Integración fina con categorías y canales RSS.
