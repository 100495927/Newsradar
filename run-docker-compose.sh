#!/bin/bash

# Exit on any individual command failure
set -e

# --- 1. Extensible List of Files ---
# Add or remove files here to change the stack composition
COMPOSE_FILES=(
  "docker-compose.yml"
  "docker-compose.mongo.yml"
  "docker-compose.rss-worker.yml" 
)

PROJECT_NAME="newsradar"

# --- 2. Build the Command Arguments ---
COMPOSE_FLAGS=""
for FILE in "${COMPOSE_FILES[@]}"; do
  if [ -f "$FILE" ]; then
    COMPOSE_FLAGS="$COMPOSE_FLAGS -f $FILE"
  else
    echo "⚠️  Warning: Config file $FILE not found. Skipping..."
  fi
done

echo "🚀 Deploying NewsRadar stack using: ${COMPOSE_FILES[*]}"

# --- 3. Run the Stack ---
docker compose -p "$PROJECT_NAME" $COMPOSE_FLAGS up --build -d

echo "✅ Stack launched!"

# --- 4. Final Status Check ---
docker compose -p "$PROJECT_NAME" $COMPOSE_FLAGS ps