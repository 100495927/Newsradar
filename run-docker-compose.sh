#!/bin/bash

set -e

PROJECT_NAME="newsradar"
COMPOSE_FILE="docker-compose.yml"

echo "Deploying NewsRadar stack using ${COMPOSE_FILE}"
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up --build -d
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" ps
