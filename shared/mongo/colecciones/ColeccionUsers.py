from .Coleccion import Coleccion
from pymongo import ASCENDING, DESCENDING

class ColeccionUsers(Coleccion):
    NOMBRE_COLECCION = "users"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": [
                "email", "first_name", "last_name", "organization", 
                "role", "status", "created_at", "updated_at"
            ],
            "properties": {
                "email": {"bsonType": "string"},
                "first_name": {"bsonType": "string"},
                "last_name": {"bsonType": "string"},
                "organization": {"bsonType": ["string", "null"]},
                "role": {"enum": ["manager", "reader"]},
                "status": {"enum": ["pending_verification", "active", "disabled"]},
                "password_hash": {"bsonType": ["string", "null"]},
                "email_verified_at": {"bsonType": ["date", "null"]},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        # Unique Email
        self._collection.create_index(
            [("email", ASCENDING)], unique=True, name="idx_users_email_unique"
        )
        # Role and Status compound index
        self._collection.create_index(
            [("role", ASCENDING), ("status", ASCENDING)], name="idx_users_role_status"
        )
