#!/usr/bin/env bash
set -euo pipefail

# Arranca el entorno Docker desde un estado limpio:
# baja el stack, limpia datastores, reconstruye sin cache y levanta recreando contenedores.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESET_SCRIPT="$SCRIPT_DIR/reset_datastores_and_rebootstrap.sh"

cd "$REPO_ROOT"

run_step() {
  local message="$1"
  shift
  echo "[arranque-limpio] $message"
  "$@"
}

run_step "Bajando stack y limpiando volumenes anonimos..." docker compose down -v --remove-orphans
run_step "Reseteando datastores persistentes..." bash "$RESET_SCRIPT"
run_step "Reconstruyendo imagenes sin cache..." docker compose build --no-cache --pull
run_step "Levantando stack limpio..." docker compose up -d --force-recreate --remove-orphans

echo "[arranque-limpio] Estado final:"
docker compose ps
