from __future__ import annotations

from datetime import datetime, timezone
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
                "id_fuente",
                "titulo",
                "autores",
                "link",
                "fecha_publicacion",
                "hash_deduplicado",
                "fecha_ingestion",
            ],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "id_fuente": {"bsonType": "objectId"},
                "titulo": {"bsonType": "string"},
                "autores": {"bsonType": ["array", "null"]},
                "link": {"bsonType": "string"},
                "categorias": {"bsonType": ["array", "null"]},
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
            [("id_fuente", 1), ("fecha_publicacion", -1)], name="idx_rss_entradas_fuente_fecha"
        )
        self._collection.create_index(
            [("fecha_publicacion", -1)], # Change to list with -1 to match init-mongo.js
            name="idx_rss_entradas_fecha_publicacion"
        )
        self._collection.create_index(
            "categorias", name="idx_rss_entradas_categorias"
        )

    def insertar(self, entrada: "RSSEntrada"):
        datos = entrada.a_mongo()
        url_fuente = entrada.fuente.url

        id_fuente = self._db_padre.col_rss_fuentes._collection.find_one({"url": url_fuente})
        if not id_fuente:
            raise ValueError(f"No se encontró la fuente en la BD para la URL: {url_fuente}")
        datos["id_fuente"] = id_fuente["_id"]
        datos.pop("fecha_ingestion")
        resultado = self._collection.update_one(
            {"hash_deduplicado": datos["hash_deduplicado"]},
            {
                "$setOnInsert": datos,
                "$set": {"fecha_ingestion": datetime.now(timezone.utc)},
            },
            upsert=True,
        )
        return resultado.upserted_id
