# Deployment Issues & Fixes

Problems encountered when running the stack for the first time with `run-docker-compose.ps1`.

---

## 1. Missing `.env` file

**Error:** `Failed to load .env: The system cannot find the file specified`

**Cause:** The repo only included `.env.example`, not the actual `.env` file that Docker Compose reads.

**Fix:** Copy `.env.example` to `.env` and fill in the required values (SMTP credentials, etc.).

---

## 2. Docker daemon not running

**Error:** `open //./pipe/docker_engine: The system cannot find the file specified`

**Cause:** Docker Desktop was not open.

**Fix:** Open Docker Desktop from the Start menu and wait for the whale icon to appear in the taskbar.

---

## 3. Docker Desktop — Unexpected WSL error

**Error:** `An unexpected error was encountered while executing a WSL command`

**Cause:** WSL lost state after a forced shutdown or sleep cycle.

**Fix:**
```powershell
wsl --shutdown
```
Then reopen Docker Desktop. If it persists, reboot the PC.

---

## 4. Docker Desktop — WSL drive missing

**Error:** `The Docker Desktop WSL data distro drive is missing`

**Cause:** The `docker-desktop-data` WSL distro was registered but its virtual disk (`.vhdx`) was missing, likely from the forced WSL shutdown.

**Fix:**
```powershell
wsl --unregister docker-desktop-data
```
Then reopen Docker Desktop. It recreates the disk from scratch. Previously created containers are lost but no project data is affected.

---

## 5. Backend container failing — `users_store` ImportError

**Error:** `ImportError: cannot import name 'users_store' from 'app.store'`

**Cause:** `alertas/routes.py` still imported `users_store`, which had been removed from `store.py` during the MongoDB migration.

**Fix:** Updated `alertas/routes.py` to import `users_col` instead and replaced the `ensure_user_exists` check to query MongoDB directly.

---

## 6. Backend Dockerfile pointing to non-existent module

**Error:** Backend crashed immediately on startup.

**Cause:** The Dockerfile CMD was `uvicorn app.main:app` but the FastAPI app is defined in `app/app.py`, not `app/main.py`.

**Fix:** Changed the Dockerfile CMD to:
```dockerfile
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 7. Elasticsearch unhealthy — disk watermark exceeded

**Error:** `high disk watermark [90%] exceeded — shards will be relocated away from this node`

**Cause:** The host machine disk was over 90% full. Elasticsearch marks the cluster as `red` and fails its healthcheck, which blocks the backend from starting.

**Fix:** Disabled disk-based shard allocation for the dev environment by adding to the Elasticsearch service in `docker-compose.yml`:
```yaml
cluster.routing.allocation.disk.threshold_enabled: false
```

---

## 8. Backend healthcheck pointing to wrong URL

**Error:** Backend container marked as unhealthy even when running correctly.

**Cause:** The healthcheck in `docker-compose.yml` was hitting `/health` but the actual route is `/api/v1/health`.

**Fix:** Updated the healthcheck URL:
```yaml
"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=2)"
```

---

## 9. Frontend 502 Bad Gateway — Vite proxy targeting localhost

**Error:** `connect ECONNREFUSED 127.0.0.1:8000`

**Cause:** The `VITE_API_BASE_URL` variable in `.env` was `http://localhost:8000`. Inside the frontend container, `localhost` refers to itself, not the backend service. This value overrode the Docker Compose default.

**Fix:** Added a separate `BACKEND_URL` variable exclusively for the internal Docker proxy target, independent of the public-facing URL:

`docker-compose.yml`:
```yaml
BACKEND_URL: http://backend:8000
```

`vite.config.js`:
```js
target: process.env.BACKEND_URL || 'http://localhost:8000'
```

This way `.env` can keep `VITE_API_BASE_URL=http://localhost:8000` for local dev without breaking Docker.

---

## 10. `passlib` incompatibility with Python 3.14

**Error:** `ValueError: password cannot be longer than 72 bytes` raised inside `passlib` during bcrypt backend initialization.

**Cause:** `passlib 1.7.4` has not been updated in years and its bcrypt backend crashes during a self-test (`detect_wrap_bug`) on Python 3.14.

**Fix:** Replaced `passlib[bcrypt]` with the `bcrypt` package directly and updated `jwt_utils.py`:
```python
import bcrypt

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

---

## 11. MongoDB schema validation rejecting user inserts

**Error:** `pymongo.errors.WriteError: Document failed validation`

**Cause:** The `users` collection was initialized by `init-mongo.js` with a JSON schema requiring fields `role`, `status`, `created_at`, `updated_at`, and `password_hash`. The backend was inserting documents with different field names (`password`, `role_ids`) and missing the required fields entirely.

**Fix:** Aligned the backend `UserInDB` model and all insert operations with the MongoDB schema:
- `password` → `password_hash`
- Removed `role_ids` (list of ints) → replaced with `role` (string enum: `"admin"`, `"manager"`, `"reader"`)
- Added `status` (string enum: `"pending_verification"`, `"active"`, `"disabled"`)
- Added `created_at` and `updated_at` timestamps to all inserts

---

## 12. Register endpoint crashing — `role_ids` attribute missing

**Error:** `AttributeError: 'UserCreate' object has no attribute 'role_ids'`

**Cause:** After removing `role_ids` from the `UserCreate` model (issue 11 fix), the register route still tried to read `payload.role_ids`.

**Fix:** Removed the `role_ids` lookup from the register route. The role is now always set to `"reader"` by default on registration.
