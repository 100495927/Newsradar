#!/usr/bin/env bash
set -euo pipefail

TYPE="${1:-all}"

case "$TYPE" in
  all|alerts|rss|worker) ;;
  *)
    echo "[worker-tests] Tipo no valido: $TYPE"
    echo "[worker-tests] Usa uno de: all, alerts, rss, worker"
    exit 1
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

write_info() {
  echo "[worker-tests] $1"
}

fail() {
  echo "[worker-tests] $1" >&2
  exit 1
}

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

export PYTHONPATH="$REPO_ROOT/rss-worker:$REPO_ROOT"

write_info "Repo: $REPO_ROOT"
write_info "Python: $PYTHON_EXE"
write_info "Tipo de tests: $TYPE"

"$PYTHON_EXE" - <<'PY'
import importlib.util
import sys

required = ["pytest", "pymongo", "feedparser", "dateparser", "croniter"]
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    print("Faltan dependencias en el entorno Python: " + ", ".join(missing))
    sys.exit(1)
PY

declare -a TARGETS
case "$TYPE" in
  all)
    TARGETS=("rss-worker/tests")
    ;;
  alerts)
    TARGETS=("rss-worker/tests/alerts")
    ;;
  rss)
    TARGETS=("rss-worker/tests/rss")
    ;;
  worker)
    TARGETS=("rss-worker/tests/worker")
    ;;
esac

write_info "Ejecutando: $PYTHON_EXE -m pytest -q ${TARGETS[*]}"
"$PYTHON_EXE" -m pytest -q "${TARGETS[@]}"
