from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .Coleccion import Coleccion

if TYPE_CHECKING:
    from rss.RSSFuente import RSSFuente


class ColeccionRssFuentes(Coleccion):
    NOMBRE_COLECCION = "rss_fuentes"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": ["hash_fuente", "medio", "url", "activo", "creado", "actualizado"],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "hash_fuente": {"bsonType": "string"},
                "medio": {"bsonType": "string"},
                "rss": {"bsonType": ["string", "null"]},
                "url": {"bsonType": "string"},
                "parser_id": {"bsonType": ["string", "null"]},
                "activo": {"bsonType": "bool"},
                "creado": {"bsonType": "date"},
                "actualizado": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "hash_fuente", unique=True, name="idx_rss_fuentes_hash_fuente_unique"
        )
        self._collection.create_index(
            "url", unique=True, name="idx_rss_fuentes_url_unique"
        )
        self._collection.create_index(
            [("medio", 1), ("rss", 1)], name="idx_rss_fuentes_medio_rss"
        )
        self._collection.create_index(
            "activo", name="idx_rss_fuentes_activo"
        )

    def insertar(self, fuente: "RSSFuente"):
        datos = fuente.a_mongo()
        ahora = datetime.now(timezone.utc)
        # Upsert idempotente por hash lógico de fuente.
        resultado = self._collection.update_one(
            {"hash_fuente": datos["hash_fuente"]},
            {
                "$set": {
                    "medio": datos["medio"],
                    "rss": datos["rss"],
                    "url": datos["url"],
                    "parser_id": datos["parser_id"],
                    "activo": datos["activo"],
                    "actualizado": ahora,
                },
                "$setOnInsert": {"creado": ahora},
            },
            upsert=True,
        )

        if resultado.upserted_id is not None:
            fuente.mongo_id = resultado.upserted_id
            return resultado.upserted_id

        doc = self._collection.find_one({"hash_fuente": datos["hash_fuente"]}, {"_id": 1})
        if not doc:
            raise ValueError("No se pudo recuperar la fuente RSS tras el upsert")

        fuente.mongo_id = doc["_id"]
        return doc["_id"]

    def lista_fuentes(self) -> list["RSSFuente"]:
        from rss.RSSFuente import RSSFuente

        return [RSSFuente.de_mongo(doc) for doc in self._collection.find()]
