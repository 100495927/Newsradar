#!/usr/bin/env python3
"""
Herramienta de sincronizacion manual/backfill MongoDB -> Elasticsearch para RSS.
Resultado esperado: los documentos de `rss_fuentes` y `rss_entradas` quedan indexados
en Elasticsearch (`rss_fuentes_idx` y `rss_entradas_idx`) de forma idempotente.
"""

from __future__ import annotations

import json
import os
from datetime import datetime

from pymongo import MongoClient
import requests


def _iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _object_id_str(value):
    if value is None:
        return None
    return str(value)


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name, default)
    if not value:
        return default
    return value


def build_bulk_lines(index_name: str, docs: list[dict], id_field: str) -> str:
    lines: list[str] = []
    for doc in docs:
        doc_id = doc[id_field]
        if not doc_id:
            continue
        lines.append(json.dumps({"index": {"_index": index_name, "_id": doc_id}}, ensure_ascii=False))
        lines.append(json.dumps(doc, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def sync() -> None:
    mongo_uri = _get_env("MONGODB_URI", "mongodb://newsradar_app:change_me_app_pwd@localhost:27017/newsradar?authSource=newsradar")
    mongo_db_name = _get_env("MONGO_DB_NAME", "newsradar")
    es_url = _get_env("ELASTICSEARCH_URL", "http://localhost:9200")
    idx_entradas = _get_env("ELASTICSEARCH_INDEX_ENTRADAS", "rss_entradas_idx")
    idx_fuentes = _get_env("ELASTICSEARCH_INDEX_FUENTES", "rss_fuentes_idx")

    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]

    fuentes_docs = []
    fuentes_por_id: dict[str, dict] = {}
    for fuente in db.rss_fuentes.find({}, {"_id": 1, "hash_fuente": 1, "medio": 1, "rss": 1, "url": 1, "parser_id": 1, "activo": 1, "creado": 1, "actualizado": 1}):
        doc_fuente = {
            "doc_id": _object_id_str(fuente["_id"]),
            "hash_fuente": fuente.get("hash_fuente"),
            "medio": fuente.get("medio"),
            "rss": fuente.get("rss"),
            "url": fuente.get("url"),
            "parser_id": fuente.get("parser_id"),
            "activo": fuente.get("activo", True),
            "creado": _iso(fuente.get("creado")),
            "actualizado": _iso(fuente.get("actualizado")),
        }
        fuentes_docs.append(doc_fuente)
        if doc_fuente["doc_id"]:
            fuentes_por_id[doc_fuente["doc_id"]] = doc_fuente

    entradas_docs = []
    for entrada in db.rss_entradas.find({}, {"_id": 0, "id_fuente": 1, "titulo": 1, "resumen": 1, "autores": 1, "link": 1, "categorias": 1, "fecha_publicacion": 1, "hash_deduplicado": 1, "fecha_ingestion": 1}):
        id_fuente = _object_id_str(entrada.get("id_fuente"))
        fuente_meta = fuentes_por_id.get(id_fuente) if id_fuente else None
        entradas_docs.append(
            {
                "doc_id": entrada.get("hash_deduplicado"),
                "id_fuente": id_fuente,
                "titulo": entrada.get("titulo"),
                "resumen": entrada.get("resumen"),
                "autores": entrada.get("autores"),
                "link": entrada.get("link"),
                "categorias": entrada.get("categorias"),
                "fecha_publicacion": _iso(entrada.get("fecha_publicacion")),
                "hash_deduplicado": entrada.get("hash_deduplicado"),
                "fecha_ingestion": _iso(entrada.get("fecha_ingestion")),
                "medio": fuente_meta.get("medio") if fuente_meta else None,
                "rss": fuente_meta.get("rss") if fuente_meta else None,
            }
        )

    fuentes_payload = build_bulk_lines(idx_fuentes, fuentes_docs, "doc_id") if fuentes_docs else None
    entradas_payload = build_bulk_lines(idx_entradas, entradas_docs, "doc_id") if entradas_docs else None

    if fuentes_payload:
        resp_fuentes = requests.post(
            f"{es_url}/_bulk",
            headers={"Content-Type": "application/x-ndjson"},
            data=fuentes_payload.encode("utf-8"),
            timeout=30,
        )
        resp_fuentes.raise_for_status()

    if entradas_payload:
        resp_entradas = requests.post(
            f"{es_url}/_bulk",
            headers={"Content-Type": "application/x-ndjson"},
            data=entradas_payload.encode("utf-8"),
            timeout=30,
        )
        resp_entradas.raise_for_status()

    print(
        f"Sincronizacion completada: {len(fuentes_docs)} fuentes y {len(entradas_docs)} entradas indexadas en Elasticsearch"
    )


if __name__ == "__main__":
    sync()
