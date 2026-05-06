from __future__ import annotations

from .Coleccion import Coleccion


class ColeccionInformationSources(Coleccion):
    NOMBRE_COLECCION = "information_sources"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": [
                "id",
                "name",
                "url",
                "active",
                "created_at",
                "updated_at",
            ],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "id": {"bsonType": ["int", "long"]},
                "name": {"bsonType": "string"},
                "url": {"bsonType": "string"},
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
            name="idx_information_sources_id_unique",
        )
        self._collection.create_index(
            "url",
            unique=True,
            # `deleted_at: null` incluye documentos activos con el campo ausente
            # y evita el uso de `$exists: false`, que falla en partial indexes
            # en algunos entornos Mongo.
            partialFilterExpression={"deleted_at": None},
            name="idx_information_sources_url_unique_active",
        )
        self._collection.create_index(
            [("active", 1), ("name", 1)],
            name="idx_information_sources_active_name",
        )


__all__ = ["ColeccionInformationSources"]
