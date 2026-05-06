from __future__ import annotations

from .Coleccion import Coleccion


class ColeccionAlerts(Coleccion):
    """
    Gestión de la colección 'alerts' en MongoDB.
    Define el esquema de validación JSON y los índices necesarios para el
    funcionamiento del motor de notificaciones.
    """

    NOMBRE_COLECCION = "alerts"

    def esquema(self):
        """
        Retorna el esquema de validación JSON (JSON Schema) para la colección.
        Garantiza que todos los documentos cumplan con los tipos de datos y campos requeridos.
        """
        return {
            "bsonType": "object",
            "required": [
                "id",
                "user_id",
                "name",
                "descriptors",
                "category_id",
                "rss_channel_ids",
                "information_sources_ids",
                "cron_expression",
                "notification_channels",
                "enabled",
                "created_at",
                "updated_at",
            ],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "id": {"bsonType": ["int", "long"]},
                "user_id": {"bsonType": ["int", "long"]},
                "name": {"bsonType": "string"},
                "descriptors": {
                    "bsonType": "array",
                    "minItems": 1,
                    "items": {"bsonType": "string"},
                },
                "categories": {
                    "bsonType": ["array", "null"],
                    "items": {
                        "bsonType": "object",
                        "properties": {
                            "code": {"bsonType": "string"},
                            "label": {"bsonType": "string"},
                        },
                    },
                },
                "category_id": {"bsonType": ["int", "long"]},
                "rss_channel_ids": {
                    "bsonType": "array",
                    "items": {"bsonType": ["int", "long"]},
                },
                "information_sources_ids": {
                    "bsonType": "array",
                    "items": {"bsonType": ["int", "long"]},
                },
                "cron_expression": {"bsonType": "string"},
                "notification_channels": {
                    "bsonType": "array",
                    "items": {"enum": ["app", "email"]},
                },
                "enabled": {"bsonType": "bool"},
                "last_checked_at": {"bsonType": ["date", "null"]},
                "last_run_at": {"bsonType": ["date", "null"]},
                "next_run_at": {"bsonType": ["date", "null"]},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        """
        Crea los índices necesarios para optimizar la búsqueda de alertas activas
        y asegurar la integridad de los IDs.
        """
        # Índice único para el ID de la alerta
        self._collection.create_index("id", unique=True, name="idx_alerts_id_unique")

        # Índice compuesto para el planificador de tareas (Scheduler)
        self._collection.create_index(
            [("user_id", 1), ("enabled", 1), ("next_run_at", 1)],
            name="idx_alerts_user_enabled_next_run",
        )

        # Índice para filtrado por categoría
        self._collection.create_index(
            [("category_id", 1), ("enabled", 1)], name="idx_alerts_category_enabled"
        )

        # Índice multikey para los canales RSS asociados
        self._collection.create_index(
            "rss_channel_ids", name="idx_alerts_rss_channel_ids"
        )
        self._collection.create_index(
            "information_sources_ids", name="idx_alerts_information_sources_ids"
        )

__all__ = ["ColeccionAlerts"]
