#!/usr/bin/env sh
# Borra todos los contenedores dockers (activo o no)

docker rm -f $(docker ps -aq)