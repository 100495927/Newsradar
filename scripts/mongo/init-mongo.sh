#!/bin/sh
# Bootstrap inicial de MongoDB para NewsRadar.
# Resultado esperado: usuario de aplicacion, colecciones RSS/usuarios y sus indices
# quedan creados al primer arranque cuando /data/db esta vacio.

set -eu

log() {
  printf '[init-mongo] %s\n' "$1"
}

fail() {
  printf '[init-mongo] ERROR: %s\n' "$1" >&2
  exit 1
}

log "Inicio de bootstrap de MongoDB"

if [ -z "${MONGO_APP_USER:-}" ] || [ -z "${MONGO_APP_PASSWORD:-}" ] || [ -z "${MONGO_APP_DB:-}" ]; then
  fail "Faltan variables MONGO_APP_USER, MONGO_APP_PASSWORD o MONGO_APP_DB"
fi

if [ -z "${MONGO_INITDB_ROOT_USERNAME:-}" ] || [ -z "${MONGO_INITDB_ROOT_PASSWORD:-}" ] || [ -z "${MONGO_INITDB_DATABASE:-}" ]; then
  fail "Faltan variables de root para bootstrap (MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD o MONGO_INITDB_DATABASE)"
fi

log "Variables de entorno validadas"
log "Conectando a mongosh para crear usuario y estructura inicial"

if ! mongosh --authenticationDatabase "$MONGO_INITDB_DATABASE" \
  -u "$MONGO_INITDB_ROOT_USERNAME" \
  -p "$MONGO_INITDB_ROOT_PASSWORD" /opt/newsradar/init-mongo.js
then
  fail "Error al ejecutar comandos en mongosh"
fi

log "Bootstrap de MongoDB finalizado correctamente"
