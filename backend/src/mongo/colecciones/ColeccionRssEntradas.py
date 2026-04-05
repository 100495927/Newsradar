from .Coleccion import Coleccion
from rss.RSSEntrada import RSSEntrada
from datetime import datetime, timezone


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
            "fecha_publicacion", name="idx_rss_entradas_fecha_publicacion"
        )
        self._collection.create_index(
            "categorias", name="idx_rss_entradas_categorias"
        )

    def insertar(self, entrada: RSSEntrada):
        datos = entrada.a_mongo()
        resultado = self._collection.update_one(
            {"hash_deduplicado": datos["hash_deduplicado"]},
            {
                "$setOnInsert": datos,
                "$set": {"fecha_ingestion": datetime.now(timezone.utc)},
            },
            upsert=True,
        )
        return resultado.upserted_id
