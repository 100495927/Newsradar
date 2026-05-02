#!/bin/sh
# Bootstrap de indices Elasticsearch para RSS.
# Resultado esperado: existen `rss_entradas_idx` y `rss_fuentes_idx` con mappings
# base para busqueda/agregacion; si ya existen, no se recrean.
set -eu

ES_URL="${ELASTICSEARCH_URL:-http://elasticsearch:9200}"
INDEX_ENTRADAS="${ELASTICSEARCH_INDEX_ENTRADAS:-rss_entradas_idx}"
INDEX_FUENTES="${ELASTICSEARCH_INDEX_FUENTES:-rss_fuentes_idx}"

wait_for_es() {
  i=0
  until [ "$i" -ge 60 ]; do
    if curl -fsS "$ES_URL/_cluster/health" >/dev/null 2>&1; then
      return 0
    fi
    i=$((i + 1))
    sleep 2
  done
  return 1
}

create_index_if_missing() {
  index_name="$1"
  mapping_payload="$2"

  status="$(curl -s -o /dev/null -w '%{http_code}' "$ES_URL/$index_name")"
  if [ "$status" = "200" ]; then
    echo "[init-elasticsearch] Indice ya existe: $index_name"
    return 0
  fi

  echo "[init-elasticsearch] Creando indice: $index_name"
  curl -fsS -X PUT "$ES_URL/$index_name" \
    -H "Content-Type: application/json" \
    -d "$mapping_payload" >/dev/null
}

if ! wait_for_es; then
  echo "[init-elasticsearch] Elasticsearch no responde a tiempo" >&2
  exit 1
fi

ENTRADAS_MAPPING='{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "analizador_rss_es": {
          "type": "standard",
          "stopwords": "_spanish_"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "hash_deduplicado": {"type": "keyword"},
      "id_fuente": {"type": "keyword"},
      "titulo": {
        "type": "text",
        "analyzer": "analizador_rss_es",
        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
      },
      "resumen": {"type": "text", "analyzer": "analizador_rss_es"},
      "autores": {"type": "keyword"},
      "link": {"type": "keyword", "index": false},
      "category_id": {"type": "integer"},
      "fecha_publicacion": {"type": "date"},
      "fecha_ingestion": {"type": "date"},
      "medio": {"type": "keyword"},
      "rss": {"type": "keyword"}
    }
  }
}'

FUENTES_MAPPING='{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "hash_fuente": {"type": "keyword"},
      "medio": {"type": "keyword"},
      "rss": {"type": "keyword"},
      "url": {"type": "keyword", "index": false},
      "parser_id": {"type": "keyword"},
      "category_id": {"type": "integer"},
      "activo": {"type": "boolean"},
      "creado": {"type": "date"},
      "actualizado": {"type": "date"}
    }
  }
}'

create_index_if_missing "$INDEX_ENTRADAS" "$ENTRADAS_MAPPING"
create_index_if_missing "$INDEX_FUENTES" "$FUENTES_MAPPING"

echo "[init-elasticsearch] Inicializacion completada"
