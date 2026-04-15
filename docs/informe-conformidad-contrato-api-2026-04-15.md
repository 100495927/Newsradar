# Inventario de Endpoints y Comparacion con Contrato AG

Fecha: 2026-04-15

Referencia contractual comparada:
- AG: docs/archivos_AG/newsradar_api/app/main.py

Implementacion comparada:
- Backend actual: backend/app/app.py y routers en backend/app/*/routes.py

Convenciones:
- AG = lo pedido en el main de referencia.
- Actual = backend refactorizado actual.
- Estado:
	- IGUAL: metodo+URI+request+response coinciden.
	- DIFERENTE: hay alguna diferencia observable.
	- EXTRA: existe en actual y no esta en AG.

## 1. Sistema

Endpoint:
- Metodo/URI: GET /api/v1/health
- AG request: sin body
- AG response: objeto con status y timestamp
- Actual request/response: igual
- Estado: IGUAL

## 2. Auth

Endpoint:
- Metodo/URI: POST /api/v1/auth/login
- AG request: LoginRequest { email, password }
- AG response: TokenResponse { access_token, token_type }
- Actual request/response: igual en shape
- Estado: IGUAL

Endpoint:
- Metodo/URI: POST /api/v1/auth/register
- AG request: UserCreate { email, first_name, last_name, organization, role_ids, password }
- AG response: User { id, email, first_name, last_name, organization, role_ids }
- Actual request: UserCreate { email, first_name, last_name, organization?, password } (sin role_ids)
- Actual response: TokenResponse { access_token, token_type }
- Estado: DIFERENTE
- Diferencia concreta:
	- Falta role_ids en request.
	- Cambia response de User a TokenResponse.

Endpoint:
- Metodo/URI: GET /api/v1/auth/verify/{token}
- AG: no existe
- Actual: existe
- Estado: EXTRA

Endpoint:
- Metodo/URI: POST /api/v1/auth/forgot-password
- AG: no existe
- Actual request: LoginRequest { email, password }
- Actual response: { message }
- Estado: EXTRA

Endpoint:
- Metodo/URI: POST /api/v1/auth/reset-password
- AG: no existe
- Actual request: query params token, new_password
- Actual response: { message }
- Estado: EXTRA

## 3. Users

Endpoint:
- Metodo/URI: GET /api/v1/users
- AG request: sin body
- AG response: List[User] con User = { id, email, first_name, last_name, organization, role_ids }
- Actual response: List[User] con User = { email, first_name, last_name, organization, role, status }
- Estado: DIFERENTE
- Diferencia concreta:
	- En actual no sale id ni role_ids.
	- En actual aparecen role y status.

Endpoint:
- Metodo/URI: POST /api/v1/users
- AG request: UserCreate con role_ids
- AG response: User con id y role_ids
- Actual request: UserCreate sin role_ids (schema), pero la ruta intenta usar payload.role_ids
- Actual response: User con role y status
- Estado: DIFERENTE
- Diferencia concreta:
	- Request y response difieren del AG.
	- Hay inconsistencia interna entre schema y uso en codigo.

Endpoint:
- Metodo/URI: GET /api/v1/users/{user_id}
- AG response: User con id y role_ids
- Actual response: User con role y status
- Estado: DIFERENTE

Endpoint:
- Metodo/URI: PUT /api/v1/users/{user_id}
- AG request: UserUpdate { email?, first_name?, last_name?, organization?, role_ids?, password? }
- AG response: User con id y role_ids
- Actual request: UserUpdate { email?, first_name?, last_name?, organization?, password? } (sin role_ids en schema)
- Actual response: User con role y status
- Estado: DIFERENTE

Endpoint:
- Metodo/URI: DELETE /api/v1/users/{user_id}
- AG request/response: sin body, 204
- Actual request/response: igual
- Estado: IGUAL

## 4. Roles

Endpoint:
- Metodo/URI: GET /api/v1/roles
- AG request: sin body
- AG response: List[Role] con Role { id, name }
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: POST /api/v1/roles
- AG request: RoleCreate { name }
- AG response: Role { id, name }
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: GET /api/v1/roles/{role_id}
- AG request/response: Role { id, name }
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: PUT /api/v1/roles/{role_id}
- AG request: RoleUpdate { name? }
- AG response: Role { id, name }
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: DELETE /api/v1/roles/{role_id}
- AG request/response: sin body, 204
- Actual request/response: igual
- Estado: IGUAL

## 5. Alerts

Endpoint:
- Metodo/URI: GET /api/v1/users/{user_id}/alerts
- AG request: sin body
- AG response: List[Alert]
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: POST /api/v1/users/{user_id}/alerts
- AG request: AlertCreate
- AG response: Alert
- Actual request/response: igual en shape
- Estado: IGUAL

Endpoint:
- Metodo/URI: GET /api/v1/users/{user_id}/alerts/{alert_id}
- AG request/response: Alert
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: PUT /api/v1/users/{user_id}/alerts/{alert_id}
- AG request: AlertUpdate
- AG response: Alert
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: DELETE /api/v1/users/{user_id}/alerts/{alert_id}
- AG request/response: sin body, 204
- Actual request/response: igual
- Estado: IGUAL

## 6. Notifications

Endpoint:
- Metodo/URI: GET /api/v1/users/{user_id}/alerts/{alert_id}/notifications
- AG request: sin body
- AG response: List[Notification]
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: POST /api/v1/users/{user_id}/alerts/{alert_id}/notifications
- AG request: NotificationCreate
- AG response: Notification
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: GET /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}
- AG request/response: Notification
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: PUT /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}
- AG request: NotificationUpdate
- AG response: Notification
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: DELETE /api/v1/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}
- AG request/response: sin body, 204
- Actual request/response: igual
- Estado: IGUAL

## 7. Categories

Endpoint:
- Metodo/URI: GET /api/v1/categories
- AG request: sin body
- AG response: List[Category]
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: POST /api/v1/categories
- AG request: CategoryCreate
- AG response: Category
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: GET /api/v1/categories/{category_id}
- AG request/response: Category
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: PUT /api/v1/categories/{category_id}
- AG request: CategoryUpdate
- AG response: Category
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: DELETE /api/v1/categories/{category_id}
- AG request/response: sin body, 204
- Actual request/response: igual
- Estado: IGUAL

## 8. Information Sources y RSS Channels

Endpoint:
- Metodo/URI: GET /api/v1/information-sources
- AG request: sin body
- AG response: List[InformationSource]
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: POST /api/v1/information-sources
- AG request: InformationSourceCreate
- AG response: InformationSource
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: GET /api/v1/information-sources/{source_id}
- AG request/response: InformationSource
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: PUT /api/v1/information-sources/{source_id}
- AG request: InformationSourceUpdate
- AG response: InformationSource
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: DELETE /api/v1/information-sources/{source_id}
- AG request/response: sin body, 204
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: GET /api/v1/information-sources/{source_id}/rss-channels
- AG request: sin body
- AG response: List[RSSChannel]
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: POST /api/v1/information-sources/{source_id}/rss-channels
- AG request: RSSChannelCreate
- AG response: RSSChannel
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: GET /api/v1/information-sources/{source_id}/rss-channels/{channel_id}
- AG request/response: RSSChannel
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: PUT /api/v1/information-sources/{source_id}/rss-channels/{channel_id}
- AG request: RSSChannelUpdate
- AG response: RSSChannel
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: DELETE /api/v1/information-sources/{source_id}/rss-channels/{channel_id}
- AG request/response: sin body, 204
- Actual request/response: igual
- Estado: IGUAL

## 9. Stats

Endpoint:
- Metodo/URI: GET /api/v1/stats
- AG request: sin body
- AG response: List[Stats]
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: POST /api/v1/stats
- AG request: StatsCreate
- AG response: Stats
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: GET /api/v1/stats/{stats_id}
- AG request/response: Stats
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: PUT /api/v1/stats/{stats_id}
- AG request: StatsUpdate
- AG response: Stats
- Actual request/response: igual
- Estado: IGUAL

Endpoint:
- Metodo/URI: DELETE /api/v1/stats/{stats_id}
- AG request/response: sin body, 204
- Actual request/response: igual
- Estado: IGUAL

## 10. Resumen rapido de diferencias

Diferencias que rompen contrato AG:
- POST /api/v1/auth/register
- GET /api/v1/users
- POST /api/v1/users
- GET /api/v1/users/{user_id}
- PUT /api/v1/users/{user_id}

Endpoints extra respecto AG (ampliaciones):
- GET /api/v1/auth/verify/{token}
- POST /api/v1/auth/forgot-password
- POST /api/v1/auth/reset-password

Todo lo demas (metodo+URI+request/response) esta alineado con AG.
