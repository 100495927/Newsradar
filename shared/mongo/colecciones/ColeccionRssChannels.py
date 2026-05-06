from __future__ import annotations

from .Coleccion import Coleccion


class ColeccionRssChannels(Coleccion):
    NOMBRE_COLECCION = "rss_channels"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": [
                "id",
                "information_source_id",
                "url",
                "category_id",
                "active",
                "created_at",
                "updated_at",
            ],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "id": {"bsonType": ["int", "long"]},
                "information_source_id": {"bsonType": ["int", "long"]},
                "url": {"bsonType": "string"},
                "category_id": {"bsonType": ["int", "long"]},
                "active": {"bsonType": "bool"},
                "deleted_at": {"bsonType": ["date", "null"]},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "id",
            unique=True,
            name="idx_rss_channels_id_unique",
        )
        self._collection.create_index(
            "url",
            unique=True,
            # `deleted_at: null` incluye documentos activos con el campo ausente
            # y evita el uso de `$exists: false`, que falla en partial indexes
            # en algunos entornos Mongo.
            partialFilterExpression={"deleted_at": None},
            name="idx_rss_channels_url_unique_active",
        )
        self._collection.create_index(
            [("information_source_id", 1), ("active", 1)],
            name="idx_rss_channels_source_active",
        )
        self._collection.create_index(
            [("category_id", 1), ("active", 1)],
            name="idx_rss_channels_category_active",
        )

    def lista_canales_activos(self):
        from rss.RSSFuente import RSSFuente

        source_docs = self._db_padre.col_information_sources._collection.find(
            {
                "active": True,
                "deleted_at": {"$exists": False},
            }
        )
        sources_by_id = {doc["id"]: doc for doc in source_docs}

        channel_docs = self._collection.find(
            {
                "active": True,
                "deleted_at": {"$exists": False},
            }
        )

        canales = []
        for doc in channel_docs:
            source_doc = sources_by_id.get(doc["information_source_id"])
            if not source_doc:
                continue
            canales.append(
                RSSFuente(
                    medio=source_doc["name"],
                    rss=doc["url"],
                    url=doc["url"],
                    activo=doc["active"],
                    category_id=doc["category_id"],
                    source_id=int(source_doc["id"]),
                    channel_id=int(doc["id"]),
                    source_url=source_doc["url"],
                )
            )
        return canales


__all__ = ["ColeccionRssChannels"]
