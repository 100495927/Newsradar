#!/usr/bin/env sh
# Herramienta de limpieza de persistencia local (MongoDB + Elasticsearch).
# Resultado esperado: se eliminan unicamente los ficheros de datos persistentes.
# No ejecuta build ni arranque de contenedores.

set -eu

echo "[reset] Limpiando datos persistentes de MongoDB y Elasticsearch..."
if [ -d "./data/mongodb/data" ]; then
  find "./data/mongodb/data" -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} +
fi
if [ -d "./data/mongodb/configdb" ]; then
  find "./data/mongodb/configdb" -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} +
fi
if [ -d "./data/elasticsearch/data" ]; then
  find "./data/elasticsearch/data" -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} +
fi

echo "[reset] Limpieza completada (solo borrado de datos)."