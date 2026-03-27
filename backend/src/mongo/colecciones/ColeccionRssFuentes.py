from .Coleccion import Coleccion
from rss.RSSFeedSource import RSSFeedSource


class ColeccionRssFuentes(Coleccion):
    NOMBRE_COLECCION = "rss_fuentes"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": ["medio", "url", "creado", "actualizado"],
            "properties": {
                "medio": {"bsonType": "string"},
                "rss": {"bsonType": ["string", "null"]},
                "url": {"bsonType": "string"},
                "parser_id": {"bsonType": "string"},
                "creado": {"bsonType": "date"},
                "actualizado": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "url", unique=True, name="idx_rss_sources_url_unique"
        )
        self._collection.create_index(
            [("medio", 1), ("rss", 1)], name="idx_rss_sources_medio_rss"
        )

    def insertar(self, fuente: RSSFeedSource):
        datos = fuente.a_mongo()
        self._collection.insert_one(datos)
