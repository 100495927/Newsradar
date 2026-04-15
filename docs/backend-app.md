# Backend App — Structure & API Reference

Entry point: `backend/app/app.py`
Run with: `uvicorn app.app:app --reload` from the `backend/` directory.

---

## Folder Structure

```
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
Single source of truth for all mutable state.

| Export | Description |
|--------|-------------|
| `roles_store` | `Dict[int, Role]` in-memory store |
| `users_store` | `Dict[int, UserInDB]` in-memory store |
| `alerts_store` | `Dict[int, Alert]` in-memory store |
| `categories_store` | `Dict[int, Category]` in-memory store |
| `notifications_store` | `Dict[int, Notification]` in-memory store |
| `information_sources_store` | `Dict[int, InformationSource]` in-memory store |
| `rss_channels_store` | `Dict[int, RSSChannel]` in-memory store |
| `stats_store` | `Dict[int, Stats]` in-memory store |
| `active_tokens` | `Dict[str, int]` bearer token → user ID |
| `users_col` | PyMongo collection for persistent user operations |
| `next_id(key)` | Auto-increment ID generator per entity type |

### `dependencies.py`
FastAPI dependencies imported by all route modules.

| Function | Description |
|----------|-------------|
| `get_current_user` | Resolves the authenticated user from a Bearer token |
| `sanitize_user` | Returns a public `User` view (no password) |
| `es_token_valido` | Checks that a token timestamp is within 24 hours |
| `ensure_gestor_role` | Raises 403 if the current user lacks the `admin` role |

---

## API Endpoints

All routes are prefixed with `/api/v1`.

### Auth — `auth/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/login` | Login with email/password, returns Bearer token |
| `POST` | `/auth/register` | Register a new user (prints verification token to logs) |
| `GET` | `/auth/verify/{token}` | Verify account email via token (expires in 24h) |
| `POST` | `/auth/forgot-password` | Generate password reset token (stored in MongoDB) |
| `POST` | `/auth/reset-password` | Reset password using a valid reset token |

### Users — `auth/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/users` | List all users (no passwords) |
| `POST` | `/users` | Create a user (authenticated) |
| `GET` | `/users/{user_id}` | Get user by ID |
| `PUT` | `/users/{user_id}` | Update user profile (own profile or admin only) |
| `DELETE` | `/users/{user_id}` | Delete user + cascade delete alerts and notifications |

### Roles — `auth/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/roles` | List all roles |
| `POST` | `/roles` | Create a role |
| `GET` | `/roles/{role_id}` | Get role by ID |
| `PUT` | `/roles/{role_id}` | Update a role |
| `DELETE` | `/roles/{role_id}` | Delete role (fails if assigned to any user) |

### Alertas — `alertas/routes.py`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/users/{user_id}/alerts` | List alerts for a user |
| `POST` | `/users/{user_id}/alerts` | Create alert (requires gestor role) |
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
