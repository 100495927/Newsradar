# Cambios IA - Roles Desactivados en Backend

Fecha: 2026-04-30
Hora: 10:00:19 +02:00

## Contexto

Se ha aplicado el cambio pedido tras la adenda: los roles dejan de tener efecto funcional en la aplicacion, pero los endpoints de roles deben seguir existiendo y responder correctamente.

## Estado encontrado antes del cambio

- En frontend no habia una logica de roles realmente activa en los flujos visibles: no habia selector de rol en registro ni pantallas claramente condicionadas por rol.
- En backend si existia logica parcial de roles:
  - alta de usuarios con `role_ids`
  - seeding de roles `manager` y `reader`
  - helper `user_has_manager_role`
  - dependencia `ensure_gestor_role`
  - restricciones sobre creacion/edicion de alertas y algunas operaciones de notificaciones
  - permisos transversales para que un `manager` pudiera acceder a recursos de otros usuarios
- Los endpoints `/roles` estaban implementados en memoria, no en MongoDB, por lo que eran buenos candidatos para mantener compatibilidad sin efecto real.
- El esquema de Mongo para usuarios seguia aceptando `manager` y `reader`.

## Decision aplicada

Se ha optado por desactivar la logica funcional de roles en backend, no por eliminar por completo sus endpoints ni el shape publico `role_ids`.

Motivos:

- La logica estaba lo bastante localizada como para neutralizarla sin rehacer demasiado contrato.
- Mantener `/roles` y `role_ids` reduce riesgo si mas adelante piden reintroducir roles.
- Eliminar sin mas el control de rol habria creado un riesgo importante: si todos pasaban a ser `manager`, un usuario podia acabar editando recursos de otros. Por eso se ha desactivado la logica de rol, pero se ha conservado el aislamiento por usuario.

## Cambios realizados

### 1. Creacion de usuarios

En `backend/app/auth/routes.py`:

- `POST /auth/register` ya no usa los `role_ids` de entrada.
- `POST /users` ya no usa los `role_ids` de entrada.
- Ambos flujos crean siempre al usuario con:
  - `role = "manager"`
  - `role_ids = [1]`
- La contrasena se persiste como `password_hash` en ambos casos.

## 2. Endpoints de roles convertidos en compatibilidad sin efecto

En `backend/app/auth/routes.py`:

- Se fija un unico rol canonico:
  - `id = 1`
  - `name = "manager"`
- `GET /roles` devuelve ese unico rol canonico.
- `POST /roles` responde correctamente pero no crea nada funcional nuevo.
- `GET /roles/{role_id}` responde correctamente para cualquier `role_id`, devolviendo nombre `manager`.
- `PUT /roles/{role_id}` responde correctamente pero no altera permisos ni persistencia real.
- `DELETE /roles/{role_id}` responde con exito pero no elimina nada funcional.

## 3. Desactivacion de la logica de rol en permisos

En `backend/app/dependencies.py`:

- `user_has_manager_role` pasa a devolver siempre `True` para mantener compatibilidad con dependencias antiguas.
- `ensure_gestor_role` deja de bloquear y simplemente devuelve el usuario autenticado.

## 4. Conservacion del aislamiento entre usuarios

Tambien en `backend/app/dependencies.py`:

- `ensure_user_can_access` ya no usa el rol para dar acceso transversal.
- Ahora solo permite acceso al propio usuario.

Esto evita una regresion de seguridad importante: si todos fueran `manager` de forma ingenua, cualquier usuario autenticado podria operar sobre recursos ajenos.

## 5. Seeding y normalizacion de datos existentes

En `backend/app/app.py`:

- Se sustituye el seeding dual `manager`/`reader` por un unico rol canonico `manager`.
- El usuario semilla `LectorDefault` deja de persistirse como `reader` y pasa tambien a `manager`.
- Se anade una normalizacion en arranque para actualizar usuarios existentes a:
  - `role = "manager"`
  - `role_ids = [1]`

## 6. Esquema Mongo

En `shared/mongo/colecciones/ColeccionUsers.py`:

- El enum del campo `role` pasa de `["manager", "reader"]` a `["manager"]`.

## 7. Ajustes menores de documentacion y mensajes

- Se actualizo la documentacion tecnica en:
  - `docs/contrato-api-backend.md`
  - `docs/backend-app.md`
- Se ajusto el docstring de creacion de alertas en `backend/app/alertas/routes.py` para que deje de afirmar que requiere rol gestor.

## Tests tocados o anadidos

- Ajustado `backend/tests/test_seed_data.py` para reflejar que todos los usuarios semilla quedan como `manager`.
- Ajustado `backend/tests/test_notification_extensions.py` por compatibilidad con validacion actual de emails.
- Anadido `backend/tests/test_roles_disabled.py` con comprobaciones especificas de:
  - ignorar `role_ids` de entrada al registrar o crear usuario
  - mantener `/roles` como no-op compatible
  - conservar el aislamiento por usuario aunque el backend trate a todos como gestores funcionales

## Verificacion realizada

Se ha ejecutado con el interprete del `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_seed_data.py backend/tests/test_roles_disabled.py backend/tests/test_auth.py backend/tests/test_alertas.py backend/tests/test_notification_extensions.py -q
```

Resultado:

- `15 passed`

## Limitaciones de verificacion

El suite completo `backend/tests` no se pudo cerrar en este entorno porque hay pruebas que dependen de servicios externos no disponibles en la sesion actual, especialmente:

- MongoDB accesible como `mongodb:27017`
- variables de entorno como `SMTP_SERVER`

Los fallos vistos en esa pasada amplia son de entorno/integracion, no de la desactivacion de roles.

## Archivos cambiados en esta actuacion

- `backend/app/alertas/routes.py`
- `backend/app/app.py`
- `backend/app/auth/routes.py`
- `backend/app/dependencies.py`
- `backend/tests/test_notification_extensions.py`
- `backend/tests/test_seed_data.py`
- `backend/tests/test_roles_disabled.py`
- `docs/backend-app.md`
- `docs/contrato-api-backend.md`
- `shared/mongo/colecciones/ColeccionUsers.py`
