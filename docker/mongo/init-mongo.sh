#!/bin/bash
set -euo pipefail

if [ -z "${MONGO_APP_USER:-}" ] || [ -z "${MONGO_APP_PASSWORD:-}" ] || [ -z "${MONGO_APP_DB:-}" ]; then
  echo "[init-mongo] Faltan variables MONGO_APP_USER, MONGO_APP_PASSWORD o MONGO_APP_DB" >&2
  exit 1
fi

mongosh --authenticationDatabase "$MONGO_INITDB_DATABASE" \
  -u "$MONGO_INITDB_ROOT_USERNAME" \
  -p "$MONGO_INITDB_ROOT_PASSWORD" <<EOF
use $MONGO_APP_DB

if (!db.getUser("$MONGO_APP_USER")) {
  db.createUser({
    user: "$MONGO_APP_USER",
    pwd: "$MONGO_APP_PASSWORD",
    roles: [{ role: "readWrite", db: "$MONGO_APP_DB" }]
  });
  print("[init-mongo] Usuario de aplicacion creado");
} else {
  print("[init-mongo] Usuario de aplicacion ya existe");
}
EOF
