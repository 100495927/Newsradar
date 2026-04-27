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
            "required": [
                "hash_fuente",
                "medio",
                "url",
                "activo",
                "creado",
                "actualizado",
            ],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "hash_fuente": {"bsonType": "string"},
                "medio": {"bsonType": "string"},
                "rss": {"bsonType": ["string", "null"]},
                "url": {"bsonType": "string"},
                "tipo": {"enum": ["source", "channel", None]},
                "activo": {"bsonType": "bool"},
                "categoria_iptc": {"bsonType": ["int", "null"]},
                "deleted_at": {"bsonType": ["date", "null"]},
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
        self._collection.create_index("activo", name="idx_rss_fuentes_activo")

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
                    "tipo": datos.get("tipo", "channel"),
                    "activo": datos["activo"],
                    "categoria_iptc": datos["categoria_iptc"],
                    "actualizado": ahora,
                },
                "$setOnInsert": {"creado": ahora},
            },
            upsert=True,
        )

        if resultado.upserted_id is not None:
            fuente.mongo_id = resultado.upserted_id
            return resultado.upserted_id

        doc = self._collection.find_one(
            {"hash_fuente": datos["hash_fuente"]}, {"_id": 1}
        )
        if not doc:
            raise ValueError("No se pudo recuperar la fuente RSS tras el upsert")

        fuente.mongo_id = doc["_id"]
        return doc["_id"]

    def lista_fuentes(self) -> list["RSSFuente"]:
        from rss.RSSFuente import RSSFuente

        query = {
            "activo": True,
            "$or": [{"tipo": "channel"}, {"tipo": {"$exists": False}}],
            "deleted_at": {"$exists": False},
        }
        return [RSSFuente.de_mongo(doc) for doc in self._collection.find(query)]

    def obtener_categoria_frecuente(self, id_fuente_obj):
        """
        Busca la categoría IPTC (int) más común entre las entradas de una fuente.
        """
        pipeline = [
            {"$match": {"id_fuente": id_fuente_obj}},
            {"$unwind": "$categorias"},
            {"$group": {"_id": "$categorias", "conteo": {"$sum": 1}}},
            {"$sort": {"conteo": -1}},
            {"$limit": 1},
        ]

        resultado = list(
            self._db_padre.col_rss_entradas._collection.aggregate(pipeline)
        )

        if resultado:
            return resultado[0]["_id"]
        return None

    def actualizar_categoria_fuente(self, url: str):
        fuente_doc = self._collection.find_one({"url": url})

        if fuente_doc and fuente_doc.get("categoria_iptc") is None:
            id_fuente = fuente_doc["_id"]
            categoria_sugerida = self.obtener_categoria_frecuente(id_fuente)

            if categoria_sugerida:
                self._collection.update_one(
                    {"_id": id_fuente},
                    {
                        "$set": {
                            "categoria_iptc": categoria_sugerida,
                            "actualizado": datetime.now(timezone.utc),
                        }
                    },
                )


__all__ = ["ColeccionRssFuentes"]
