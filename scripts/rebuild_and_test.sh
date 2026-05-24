#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESET_SCRIPT="$SCRIPT_DIR/reset_datastores_and_rebootstrap.sh"
TEST_RUNNER="$REPO_ROOT/devops_verifica-main/run_tests.py"

cd "$REPO_ROOT"

timeout_seconds="${TIMEOUT_SECONDS:-600}"
poll_seconds="${POLL_SECONDS:-5}"
services=(mongodb rss-worker alert-worker backend frontend)
test_args=("$@")
total_start="$(date +%s)"
timing_names=()
timing_values=()

run_step() {
  local message="$1"
  shift
  echo "[rebuild-test] $message"
  "$@"
}

show_compose_status() {
  echo "[rebuild-test] Estado actual de contenedores:"
  docker compose ps
}

format_duration() {
  local seconds="$1"
  local hours=$((seconds / 3600))
  local minutes=$(((seconds % 3600) / 60))
  local secs=$((seconds % 60))
  printf "%02d:%02d:%02d" "$hours" "$minutes" "$secs"
}

record_timing() {
  timing_names+=("$1")
  timing_values+=("$2")
}

show_timing_summary() {
  local exit_code="$1"
  local total_elapsed=$(($(date +%s) - total_start))
  echo
  echo "[rebuild-test] Resumen de tiempos:"
  for i in "${!timing_names[@]}"; do
    printf "[rebuild-test]   %-18s %s\n" "${timing_names[$i]}" "$(format_duration "${timing_values[$i]}")"
  done
  printf "[rebuild-test]   %-18s %s\n" "total" "$(format_duration "$total_elapsed")"
  echo "[rebuild-test] Exit code: $exit_code"
}

measure_step() {
  local name="$1"
  shift
  local start
  start="$(date +%s)"
  "$@"
  local exit_code="$?"
  record_timing "$name" "$(($(date +%s) - start))"
  return "$exit_code"
}

get_container_id() {
  docker compose ps -q "$1" 2>/dev/null | head -n 1
}

get_state() {
  docker inspect -f '{{.State.Status}}' "$1" 2>/dev/null || true
}

get_health() {
  docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$1" 2>/dev/null || true
}

cleanup_phase() {
  run_step "Bajando stack y eliminando volumenes anonimos..." docker compose down -v
  run_step "Borrando datos persistentes locales..." bash "$RESET_SCRIPT"
}

build_phase() {
  run_step "Reconstruyendo imagenes sin cache..." docker compose build --no-cache --pull
}

up_phase() {
  run_step "Levantando stack con recreacion forzada..." docker compose up -d --force-recreate

  local deadline=$((SECONDS + timeout_seconds))
  all_healthy=0
  while [ "$SECONDS" -lt "$deadline" ]; do
    all_healthy=1

    for svc in "${services[@]}"; do
      cid="$(get_container_id "$svc")"
      if [ -z "$cid" ]; then
        all_healthy=0
        break
      fi

      state="$(get_state "$cid")"
      health="$(get_health "$cid")"

      if [ "$state" != "running" ]; then
        all_healthy=0
        break
      fi

      if [ -n "$health" ] && [ "$health" != "healthy" ]; then
        if [ "$health" = "unhealthy" ]; then
          echo "[rebuild-test] Service $svc is unhealthy." >&2
          return 1
        fi
        all_healthy=0
        break
      fi
    done

    if [ "$all_healthy" -eq 1 ]; then
      return 0
    fi

    sleep "$poll_seconds"
  done

  show_compose_status
  echo "[rebuild-test] Timeout waiting for compose services to become healthy." >&2
  return 1
}

test_phase() {
  if [ ! -f "$TEST_RUNNER" ]; then
    echo "[rebuild-test] No se encontro el runner de tests en $TEST_RUNNER" >&2
    return 1
  fi

  echo "[rebuild-test] Servicios sanos. Ejecutando tests: python $TEST_RUNNER ${test_args[*]:-}"
  python "$TEST_RUNNER" "${test_args[@]}"
}

exit_code=0

measure_step "borrar" cleanup_phase || exit_code="$?"
if [ "$exit_code" -eq 0 ]; then
  measure_step "build" build_phase || exit_code="$?"
fi
if [ "$exit_code" -eq 0 ]; then
  measure_step "levantar" up_phase || exit_code="$?"
fi
if [ "$exit_code" -eq 0 ]; then
  show_compose_status
  measure_step "tests" test_phase || exit_code="$?"
fi

show_timing_summary "$exit_code"
exit "$exit_code"
