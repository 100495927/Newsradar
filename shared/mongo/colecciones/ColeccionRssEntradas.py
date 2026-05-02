from __future__ import annotations

from typing import TYPE_CHECKING

from .Coleccion import Coleccion

if TYPE_CHECKING:
    from rss.RSSEntrada import RSSEntrada

class ColeccionRssEntradas(Coleccion):
    NOMBRE_COLECCION = "rss_entradas"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": [
                "information_source_id",
                "rss_channel_id",
                "titulo",
                "autores",
                "link",
                "fecha_publicacion",
                "hash_deduplicado",
                "fecha_ingestion",
            ],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "information_source_id": {"bsonType": ["int", "long"]},
                "rss_channel_id": {"bsonType": ["int", "long"]},
                "source_name": {"bsonType": ["string", "null"]},
                "source_url": {"bsonType": ["string", "null"]},
                "channel_url": {"bsonType": ["string", "null"]},
                "titulo": {"bsonType": "string"},
                "autores": {"bsonType": ["array", "null"]},
                "link": {"bsonType": "string"},
                "category_id": {"bsonType": ["int", "null"]},
                "resumen": {"bsonType": ["string", "null"]},
                "fecha_publicacion": {"bsonType": "date"},
                "hash_deduplicado": {"bsonType": "string"},
                "fecha_ingestion": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "hash_deduplicado", unique=True, name="idx_rss_entradas_hash_deduplicado_unique"
        )
        self._collection.create_index(
            [("rss_channel_id", 1), ("fecha_publicacion", -1)],
            name="idx_rss_entradas_channel_fecha",
        )
        self._collection.create_index(
            [("information_source_id", 1), ("fecha_publicacion", -1)],
            name="idx_rss_entradas_source_fecha",
        )
        self._collection.create_index(
            [("fecha_publicacion", -1)], # Change to list with -1 to match init-mongo.js
            name="idx_rss_entradas_fecha_publicacion"
        )
        self._collection.create_index(
            "category_id", name="idx_rss_entradas_category_id"
        )

    def insertar(self, entrada: "RSSEntrada"):
        datos = entrada.a_mongo()
        if datos.get("information_source_id") is None:
            raise ValueError("La entrada RSS no incluye information_source_id")
        if datos.get("rss_channel_id") is None:
            raise ValueError("La entrada RSS no incluye rss_channel_id")
        resultado = self._collection.update_one(
            {"hash_deduplicado": datos["hash_deduplicado"]},
            {"$setOnInsert": datos},
            upsert=True,
        )
        return resultado.upserted_id

__all__ = ["ColeccionRssEntradas"]
