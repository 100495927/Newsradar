# Backend App — Structure & API Reference

Entry point: `backend/app/app.py`
Run with: `uvicorn app.app:app --reload` from the `backend/` directory.

---

## Folder Structure

```text
backend/app/
├── app.py               # FastAPI app: registers all routers, seed data, /health
├── store.py             # Shared state: in-memory stores + MongoDB connection
├── dependencies.py      # Shared FastAPI dependencies used across modules
│
├── auth/                # Authentication, users and roles
│   ├── user.py          # Pydantic models: Role*, User*, LoginRequest, TokenResponse
│   └── routes.py        # Auth routes + Users CRUD + Roles CRUD
│
├── alertas/             # Alerts per user
│   ├── models.py        # AlertCategoryItem, Alert*
│   └── routes.py        # Alert CRUD
│
├── notificaciones/      # Notifications per alert
│   ├── models.py        # Notification* (imports Metric from stats)
│   └── routes.py        # Notification CRUD
│
├── rss/                 # Information sources and their RSS channels
│   ├── models.py        # InformationSource* + RSSChannel*
│   └── routes.py        # InformationSource CRUD + RSSChannel CRUD
│
├── category/            # IPTC categories
│   ├── models.py        # Category*
│   └── routes.py        # Category CRUD
│
└── stats/               # Statistics and metrics
    ├── models.py        # Metric + Stats*
    └── routes.py        # Stats CRUD
```

---

## Shared Files

### `store.py`
Shared persistence and runtime state.

| Export | Description |
|--------|-------------|
| `roles_store` | `Dict[int, Role]` in-memory store used only for API compatibility |
| `categories_store` | `Dict[int, Category]` in-memory store |
| `users_col` | PyMongo collection for users |
| `information_sources_col` | PyMongo collection for information sources |
| `rss_channels_col` | PyMongo collection for RSS channels |
| `rss_entradas_col` | PyMongo collection for ingested RSS entries |
| `stats_col` | PyMongo collection for stats |
| `alerts_col` | PyMongo collection for alerts |
| `notifications_col` | PyMongo collection for notifications |
| `counters_col` | PyMongo collection for persistent integer counters |
| `next_id(key)` | Auto-increment ID generator per entity type |
| `next_mongo_id(key)` | Persistent MongoDB-backed ID generator |

Current persistence split:

- MongoDB: users, `information_sources`, `rss_channels`, `rss_entradas`, alerts, notifications, stats and counters
- In-memory: categories and a canonical `manager` role used only for compatibility

### `dependencies.py`
FastAPI dependencies imported by all route modules.

| Function | Description |
|----------|-------------|
| `get_current_user` | Resolves the authenticated user from a JWT Bearer token |
| `sanitize_user` | Returns a public `User` view (no password) |
| `es_token_valido` | Checks that a token timestamp is within 24 hours |
| `ensure_gestor_role` | Compatibility dependency; no longer blocks authenticated users |

### `app.py`

- Registers the modular routers under `/api/v1`
- Configures CORS for `http://localhost:5173`
- Exposes `GET /api/v1/health`
- Contains seed helpers that normalize all users to the functional `manager` role and create/update the default `AdminDefault`, `GestorDefault` and `LectorDefault` users accordingly.

---

## API Endpoints

All routes are prefixed with `/api/v1`.

### Auth — `auth/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/login` | Login with email/password, returns Bearer token |
| `POST` | `/auth/register` | Register a new user, returns the created public `User` |
| `GET` | `/auth/verify/{token}` | Verify account email via token (expires in 24h) |
| `POST` | `/auth/forgot-password` | Generate password reset token in MongoDB |
| `POST` | `/auth/reset-password` | Reset password using `token` and `new_password` query params |

### Users — `auth/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/users` | List all users (no passwords) |
| `POST` | `/users` | Create a user (authenticated) |
| `GET` | `/users/{user_id}` | Get user by ID |
| `PUT` | `/users/{user_id}` | Update user profile (own profile only) |
| `DELETE` | `/users/{user_id}` | Delete user + cascade delete alerts and notifications |

### Roles — `auth/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/roles` | Return the canonical `manager` role |
| `POST` | `/roles` | Compatibility no-op that returns `manager` |
| `GET` | `/roles/{role_id}` | Compatibility read; echoes the requested ID as `manager` |
| `PUT` | `/roles/{role_id}` | Compatibility no-op that returns `manager` |
| `DELETE` | `/roles/{role_id}` | Compatibility no-op with `204 No Content` |

### Alertas — `alertas/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/users/{user_id}/alerts` | List alerts for a user |
| `POST` | `/users/{user_id}/alerts` | Create alert |
| `GET` | `/users/{user_id}/alerts/{alert_id}` | Get a specific alert |
| `PUT` | `/users/{user_id}/alerts/{alert_id}` | Update an alert |
| `DELETE` | `/users/{user_id}/alerts/{alert_id}` | Delete alert + cascade delete notifications |

### Notificaciones — `notificaciones/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/users/{user_id}/alerts/{alert_id}/notifications` | List notifications for an alert |
| `POST` | `/users/{user_id}/alerts/{alert_id}/notifications` | Create a notification |
| `GET` | `/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}` | Get a notification |
| `PUT` | `/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}` | Update a notification |
| `DELETE` | `/users/{user_id}/alerts/{alert_id}/notifications/{notification_id}` | Delete a notification |

### RSS — `rss/routes.py`

#### Information Sources

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/information-sources` | List all information sources |
| `POST` | `/information-sources` | Create an information source |
| `GET` | `/information-sources/{source_id}` | Get source by ID |
| `PUT` | `/information-sources/{source_id}` | Update a source |
| `DELETE` | `/information-sources/{source_id}` | Delete source + cascade delete its RSS channels |

#### RSS Channels

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/information-sources/{source_id}/rss-channels` | List RSS channels for a source |
| `POST` | `/information-sources/{source_id}/rss-channels` | Create an RSS channel (validates category) |
| `GET` | `/information-sources/{source_id}/rss-channels/{channel_id}` | Get a channel |
| `PUT` | `/information-sources/{source_id}/rss-channels/{channel_id}` | Update a channel |
| `DELETE` | `/information-sources/{source_id}/rss-channels/{channel_id}` | Delete a channel |

### Category — `category/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/categories` | List all categories |
| `POST` | `/categories` | Create a category (source must be `IPTC`) |
| `GET` | `/categories/{category_id}` | Get category by ID |
| `PUT` | `/categories/{category_id}` | Update a category |
| `DELETE` | `/categories/{category_id}` | Delete category (fails if linked to RSS channels) |

### Stats — `stats/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/stats` | List all stats records |
| `POST` | `/stats` | Create a stats record (contains a list of `Metric`) |
| `GET` | `/stats/{stats_id}` | Get a stats record by ID |
| `PUT` | `/stats/{stats_id}` | Update a stats record |
| `DELETE` | `/stats/{stats_id}` | Delete a stats record |

### System — `app.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Healthcheck — returns status and UTC timestamp |

---

## Current Status: Alerts and Notifications

The backend keeps the original AG contract for `Alert` and `Notification`, and stores the worker-facing alert state in MongoDB.

- `alerts` now persists `cron_expression`, `enabled`, `last_checked_at`, `last_run_at` and `next_run_at`
- `notifications` persists the generated matches plus internal delivery fields such as `delivery_channels`, `email_status`, `email_sent_at`, `email_error` and `read_at`
- the normal contractual routes are still available for alerts and notifications
- the delivery configuration per alert and the user mailbox routes are documented as backend extensions outside the original contract in `docs/contrato-api-backend.md`
- the backend writes alert state to MongoDB, while `alert-worker` is responsible for processing due alerts and delivering notifications

## Notes

- `auth/routes.py` currently owns three groups of endpoints: auth, users and roles.
- The runtime contract is defined by the modular backend, not by the old monolithic AG reference file.
- If you need the contract-oriented view with reconciliation notes against the AG version, use `docs/contrato-api-backend.md`.
