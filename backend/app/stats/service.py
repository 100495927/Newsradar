from __future__ import annotations

import re
from collections import Counter
from typing import Any

from ..store import alerts_col, rss_entradas_col, rss_fuentes_col

STOPWORDS = {
    "como",
    "con",
    "del",
    "el",
    "en",
    "la",
    "las",
    "los",
    "para",
    "que",
    "una",
    "uno",
}


def get_global_stats() -> dict[str, Any]:
    """Realiza agregaciones en MongoDB para el dashboard global."""
    alertas_por_categoria = list(
        alerts_col.aggregate(
            [
                {"$unwind": "$categories"},
                {"$group": {"_id": "$categories.label", "total": {"$sum": 1}}},
                {"$project": {"_id": 0, "id": "$_id", "total": 1}},
                {"$sort": {"total": -1, "id": 1}},
            ]
        )
    )
    noticias_por_categoria = list(
        rss_entradas_col.aggregate(
            [
                {"$unwind": "$categorias"},
                {"$group": {"_id": "$categorias", "total": {"$sum": 1}}},
                {"$project": {"_id": 0, "id": "$_id", "total": 1}},
                {"$sort": {"total": -1, "id": 1}},
            ]
        )
    )

    return {
        "n_fuentes": _count_active_feed_channels(),
        "n_canales_rss": _count_all_rss_channels(),
        "n_noticias": rss_entradas_col.count_documents({}),
        "n_alertas": alerts_col.count_documents({}),
        "alertas_por_categoria": _stringify_category_ids(alertas_por_categoria),
        "noticias_por_categoria": _stringify_category_ids(noticias_por_categoria),
    }


def get_feed_stats(feed_id: int) -> dict[str, int]:
    """Calcula estadisticas para un canal RSS del contrato API."""
    fuente = rss_fuentes_col.find_one(
        {
            "tipo": "channel",
            "channel_id": feed_id,
            "deleted_at": {"$exists": False},
        },
        {"_id": 1},
    )
    noticias_query = {"id_fuente": fuente["_id"]} if fuente else {"_id": "__missing__"}
    return {
        "feed_id": feed_id,
        "n_noticias": rss_entradas_col.count_documents(noticias_query),
        "n_alertas": alerts_col.count_documents({"rss_channel_ids": feed_id}),
    }


def get_word_cloud_data(categoria: str) -> list[dict[str, int | str]]:
    """Genera una nube de palabras desde noticias RSS de una categoria."""
    category_values = [categoria]
    if categoria.isdigit():
        category_values.append(int(categoria))

    cursor = rss_entradas_col.find(
        {"categorias": {"$in": category_values}},
        {"titulo": 1, "resumen": 1},
    )
    texto_completo = " ".join(
        f"{entry.get('titulo', '')} {entry.get('resumen', '')}" for entry in cursor
    )

    palabras = re.findall(r"\w+", texto_completo.lower())
    palabras_filtradas = [
        palabra for palabra in palabras if palabra not in STOPWORDS and len(palabra) > 3
    ]

    return [
        {"word": word, "value": count}
        for word, count in Counter(palabras_filtradas).most_common(50)
    ]


def get_timeline_stats() -> list[dict[str, Any]]:
    """Noticias ingestionadas por dia agrupadas por fecha (ultimos 30 dias)."""
    return list(
        rss_entradas_col.aggregate(
            [
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$fecha_ingestion",
                            }
                        },
                        "total": {"$sum": 1},
                    }
                },
                {"$project": {"_id": 0, "fecha": "$_id", "total": 1}},
                {"$sort": {"fecha": 1}},
                {"$limit": 30},
            ]
        )
    )


def _count_active_feed_channels() -> int:
    return rss_fuentes_col.count_documents(
        {
            "activo": True,
            "$or": [{"tipo": "channel"}, {"tipo": {"$exists": False}}],
            "deleted_at": {"$exists": False},
        }
    )


def _count_all_rss_channels() -> int:
    return rss_fuentes_col.count_documents(
        {
            "$or": [{"tipo": "channel"}, {"tipo": {"$exists": False}}],
            "deleted_at": {"$exists": False},
        }
    )


def _stringify_category_ids(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for item in items:
        item["id"] = str(item.get("id", ""))
    return items
