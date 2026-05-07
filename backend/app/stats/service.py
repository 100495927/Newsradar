from __future__ import annotations

import re
from collections import Counter
from typing import Any

from ..store import alerts_col, information_sources_col, rss_channels_col, rss_entradas_col

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
    "este", 
    "esta", 
    "estos", 
    "estas", 
    "pero", 
    "sus", 
    "les",
    "desde", 
    "entre", 
    "cuando", 
    "todo", 
    "todos", 
    "sobre", 
    "haber", 
    "donde", 
    "está", 
    "están", 
    "tiene", 
    "tienen", 
    "hace", 
    "hacer"
}


def get_global_stats() -> dict[str, Any]:
    """Realiza agregaciones para el dashboard global (Objetivo 6.b)."""
    # 1. Agregación de Alertas por categoría
    alertas_por_categoria = list(
        alerts_col.aggregate([
            {"$group": {"_id": "$category_id", "total": {"$sum": 1}}},
            {"$project": {"_id": 0, "id": "$_id", "total": 1}},
            {"$sort": {"total": -1, "id": 1}},
        ])
    )
    
    # 2. Agregación de Noticias por categoría
    noticias_por_categoria = list(
        rss_entradas_col.aggregate([
            {"$match": {"category_id": {"$ne": None}}},
            {"$group": {"_id": "$category_id", "total": {"$sum": 1}}},
            {"$project": {"_id": 0, "id": "$_id", "total": 1}},
            {"$sort": {"total": -1, "id": 1}},
        ])
    )

    # Respuesta completa con recuentos de fuentes, canales, noticias y alertas
    return {
        "n_fuentes": _count_active_information_sources(),
        "n_canales_rss": _count_all_rss_channels(),
        "n_noticias": rss_entradas_col.count_documents({}),
        "n_alertas": alerts_col.count_documents({}),
        "alertas_por_categoria": _stringify_category_ids(alertas_por_categoria),
        "noticias_por_categoria": _stringify_category_ids(noticias_por_categoria),
    }


def get_feed_stats(feed_id: int) -> dict[str, Any]:
    """Calcula estadísticas para un canal RSS específico."""
    channel = rss_channels_col.find_one(
        {
            "id": feed_id,
            "deleted_at": {"$exists": False},
        },
        {"id": 1},
    )

    noticias_query = {"rss_channel_id": feed_id} if channel else {"_id": "__missing__"}
    
    return {
        "feed_id": feed_id,
        "n_noticias": rss_entradas_col.count_documents(noticias_query),
        "n_alertas": alerts_col.count_documents({"rss_channel_ids": feed_id})
    }


def get_word_cloud_data(categoria: str) -> list[dict[str, int | str]]:
    """Genera nube de palabras limpia de HTML y basura (Objetivo 6.a)."""
    category_values = [categoria]
    if categoria.isdigit():
        category_values.append(int(categoria))

    cursor = rss_entradas_col.find(
        {"category_id": {"$in": category_values}},
        {"titulo": 1, "resumen": 1},
    )

    textos = []
    for entry in cursor:
        raw_text = f"{entry.get('titulo', '')} {entry.get('resumen', '')}"
        
        # 1. Eliminar etiquetas HTML
        text_no_html = re.sub(r'<.*?>', '', raw_text)
        # 2. Eliminar entidades HTML (ej: &nbsp;)
        text_no_entities = re.sub(r'&[a-z0-9]+;', ' ', text_no_html)
        textos.append(text_no_entities)

    texto_completo = " ".join(textos).lower()
    
    # Extraer palabras alfanuméricas
    palabras = re.findall(r"\w+", texto_completo)
    
    # Filtrado: longitud > 3, no números sueltos y no stopwords
    palabras_filtradas = [
        p for p in palabras 
        if p not in STOPWORDS and len(p) > 3 and not p.isdigit()
    ]

    return [
        {"word": word, "value": count}
        for word, count in Counter(palabras_filtradas).most_common(50)
    ]


def get_timeline_stats() -> list[dict[str, Any]]:
    """Noticias capturadas por día en los últimos 30 días."""
    return list(
        rss_entradas_col.aggregate([
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
        ])
    )

def _count_active_information_sources() -> int:
    """Cuenta fuentes activas no borradas."""
    return information_sources_col.count_documents({
        "active": True,
        "deleted_at": {"$exists": False},
    })

def _count_all_rss_channels() -> int:
    """Cuenta todos los canales RSS no borrados."""
    return rss_channels_col.count_documents({
        "deleted_at": {"$exists": False},
    })

def _stringify_category_ids(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Asegura que los IDs de categoría sean strings para el frontend."""
    for item in items:
        item["id"] = str(item.get("id", ""))
    return items
