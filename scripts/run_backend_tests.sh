#!/usr/bin/env bash
set -euo pipefail

TYPE="${1:-all}"
SKIP_MONGO_CHECK="${SKIP_MONGO_CHECK:-0}"

case "$TYPE" in
  all|unit|integration|api|email) ;;
  *)
    echo "[tests] Tipo no valido: $TYPE"
    echo "[tests] Usa uno de: all, unit, integration, api, email"
    exit 1
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

write_info() {
  echo "[tests] $1"
}

fail() {
  echo "[tests] $1" >&2
  exit 1
}

load_dotenv() {
  local env_path="$1"
  if [[ ! -f "$env_path" ]]; then
    return
  fi

  while IFS= read -r line; do
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" || "${line:0:1}" == "#" ]] && continue
    if [[ "$line" == *"="* ]]; then
      export "${line%%=*}"="${line#*=}"
    fi
  done < "$env_path"
}

load_dotenv "$REPO_ROOT/.env"

if [[ -x "$REPO_ROOT/.venv/Scripts/python.exe" ]]; then
  PYTHON_EXE="$REPO_ROOT/.venv/Scripts/python.exe"
elif [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON_EXE="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_EXE="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_EXE="$(command -v python)"
else
  fail "No encuentro Python. Crea el virtualenv en .venv o instala Python."
fi

export PYTHONPATH="$REPO_ROOT/backend:$REPO_ROOT"
export MONGO_HOST="${MONGO_HOST:-localhost}"
export MONGO_PORT="${MONGO_PORT:-27017}"
export MONGO_APP_USER="${MONGO_APP_USER:-newsradar_app}"
export MONGO_APP_PASSWORD="${MONGO_APP_PASSWORD:-change_me_app_pwd}"
export MONGO_APP_DB="${MONGO_APP_DB:-newsradar}"

if [[ "$MONGO_HOST" == "mongodb" ]]; then
  export MONGO_HOST="localhost"
fi

export MONGODB_URI="mongodb://${MONGO_APP_USER}:${MONGO_APP_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}/${MONGO_APP_DB}?authSource=${MONGO_APP_DB}"

write_info "Repo: $REPO_ROOT"
write_info "Python: $PYTHON_EXE"
write_info "Tipo de tests: $TYPE"
write_info "Mongo esperado en ${MONGO_HOST}:${MONGO_PORT}"

"$PYTHON_EXE" - <<'PY'
import importlib.util
import sys

required = ["pytest", "croniter", "pymongo", "fastapi", "httpx"]
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    print("Faltan dependencias en el entorno Python: " + ", ".join(missing))
    sys.exit(1)
PY

if [[ "$TYPE" != "unit" && "$SKIP_MONGO_CHECK" != "1" ]]; then
  write_info "Comprobando conectividad con MongoDB..."
  "$PYTHON_EXE" - <<'PY'
import os
import sys
from pymongo import MongoClient

uri = os.environ["MONGODB_URI"]
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
except Exception as exc:
    print(f"No se pudo conectar a MongoDB con {uri}: {exc}")
    sys.exit(1)
PY
fi

declare -a TARGETS
case "$TYPE" in
  all)
    TARGETS=("backend/tests")
    ;;
  unit)
    TARGETS=(
      "backend/tests/test_auth.py"
      "backend/tests/test_alertas.py::test_modelo_alerta_invalido"
    )
    ;;
  integration)
    TARGETS=(
      "backend/tests/test_stats.py"
      "backend/tests/test_rss.py"
      "backend/tests/test_api_features.py"
      "backend/tests/test_seed_data.py"
      "backend/tests/test_notification_extensions.py"
      "backend/tests/test_roles_disabled.py"
      "backend/tests/test_alertas.py::test_health_endpoint"
      "backend/tests/test_alertas.py::test_crear_alerta_requiere_autenticacion"
    )
    ;;
  api)
    TARGETS=("backend/tests/api")
    ;;
  email)
    TARGETS=("backend/tests/test_email_send.py")
    ;;
esac

write_info "Ejecutando: $PYTHON_EXE -m pytest -q ${TARGETS[*]}"
"$PYTHON_EXE" -m pytest -q "${TARGETS[@]}"
