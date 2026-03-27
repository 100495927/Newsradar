from .Coleccion import Coleccion
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
                "id_fuente": {"bsonType": "string"},
                "titulo": {"bsonType": "string"},
                "autores": {"bsonType": ["array", "null"]},
                "link": {"bsonType": "string"},
                "fecha_publicacion": {"bsonType": "date"},
                "hash_deduplicado": {"bsonType": "string"},
                "fecha_ingestion": {"bsonType": "date"},
                "categories": {"bsonType": ["array", "null"]},
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "hash_deduplicado", unique=True, name="idx_rss_items_dedup_unique"
        )
        self._collection.create_index(
            [("source_id", 1), ("published_at", -1)], name="idx_rss_items_source_date"
        )

    def insertar(self, entrada: RSSEntrada):
        datos = entrada.a_mongo()
        self._collection.insert_one(datos)
