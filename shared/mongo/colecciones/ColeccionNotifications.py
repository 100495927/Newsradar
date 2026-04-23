from __future__ import annotations

from .Coleccion import Coleccion

class ColeccionNotifications(Coleccion):
    """
    Gestión de la colección 'notifications' en MongoDB.
    Almacena el registro de todas las notificaciones generadas por las alertas,
    incluyendo el estado del envío por email y los matches de noticias.
    """
    NOMBRE_COLECCION = "notifications"

    def esquema(self):
        """
        Retorna el esquema de validación JSON para las notificaciones.
        Define una estructura compleja que incluye arrays de objetos para métricas y resultados.
        """
        return {
            "bsonType": "object",
            "required": [
                "id",
                "alert_id",
                "user_id",
                "timestamp",
                "subject",
                "metrics",
                "matches",
                "delivery_channels",
                "email_status",
                "created_at",
            ],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "id": {"bsonType": ["int", "long"]},
                "alert_id": {"bsonType": ["int", "long"]},
                "user_id": {"bsonType": ["int", "long"]},
                "timestamp": {"bsonType": "date"},
                "subject": {"bsonType": "string"},
                "metrics": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "required": ["name", "value"],
                        "properties": {
                            "name": {"bsonType": "string"},
                            "value": {"bsonType": ["double", "int", "long", "decimal"]},
                        },
                    },
                },
                "matches": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "required": [
                            "title",
                            "link",
                            "source",
                            "published_at",
                            "summary",
                            "matched_descriptors",
                        ],
                        "properties": {
                            "rss_entry_id": {"bsonType": ["objectId", "null"]},
                            "rss_entry_hash": {"bsonType": ["string", "null"]},
                            "title": {"bsonType": "string"},
                            "link": {"bsonType": "string"},
                            "source": {"bsonType": ["string", "null"]},
                            "published_at": {"bsonType": ["date", "null"]},
                            "summary": {"bsonType": ["string", "null"]},
                            "matched_descriptors": {
                                "bsonType": "array",
                                "items": {"bsonType": "string"},
                            },
                            "category_id": {"bsonType": ["int", "long", "null"]},
                        },
                    },
                },
                "delivery_channels": {
                    "bsonType": "array",
                    "items": {"enum": ["app", "email"]},
                },
                "email_status": {"enum": ["pending", "sent", "failed", "skipped"]},
                "email_sent_at": {"bsonType": ["date", "null"]},
                "email_error": {"bsonType": ["string", "null"]},
                "read_at": {"bsonType": ["date", "null"]},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": ["date", "null"]},
            },
        }

    def crear_indices(self):
        """
        Crea los índices necesarios para la gestión de notificaciones y rendimiento de consultas por usuario.
        """
        # ID único de notificación
        self._collection.create_index(
            "id", unique=True, name="idx_notifications_id_unique"
        )
        
        # Consultas de historial por alerta cronológico
        self._collection.create_index(
            [("alert_id", 1), ("timestamp", -1)], 
            name="idx_notifications_alert_timestamp"
        )
        
        # Consultas para la bandeja de entrada del usuario (pendientes de leer)
        self._collection.create_index(
            [("user_id", 1), ("read_at", 1), ("timestamp", -1)], 
            name="idx_notifications_user_read_timestamp"
        )
        
        # Índice para el worker de envío de correos
        self._collection.create_index(
            [("email_status", 1), ("created_at", 1)], 
            name="idx_notifications_email_status_created"
        )

__all__ = ["ColeccionNotifications"]