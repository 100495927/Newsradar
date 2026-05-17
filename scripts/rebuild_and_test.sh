#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESET_SCRIPT="$SCRIPT_DIR/reset_datastores_and_rebootstrap.sh"

cd "$REPO_ROOT"

echo "[rebuild-test] docker compose down..."
docker compose down

echo "[rebuild-test] Resetting datastores..."
bash "$RESET_SCRIPT"

echo "[rebuild-test] Building and starting compose..."
docker compose up -d --build

services=(mongodb rss-worker alert-worker backend frontend)

timeout_seconds="${TIMEOUT_SECONDS:-600}"
poll_seconds="${POLL_SECONDS:-5}"

deadline=$((SECONDS + timeout_seconds))

get_container_id() {
  docker compose ps -q "$1" 2>/dev/null | head -n 1
}

get_state() {
  docker inspect -f '{{.State.Status}}' "$1" 2>/dev/null || true
}

get_health() {
  docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "$1" 2>/dev/null || true
}

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
        exit 1
      fi
      all_healthy=0
      break
    fi
  done

  if [ "$all_healthy" -eq 1 ]; then
    break
  fi

  sleep "$poll_seconds"
done

if [ "$all_healthy" -ne 1 ]; then
  echo "[rebuild-test] Timeout waiting for compose services to become healthy." >&2
  exit 1
fi

echo "[rebuild-test] All services healthy. Running test suite..."
python ./devops_verifica-main/run_tests.py
