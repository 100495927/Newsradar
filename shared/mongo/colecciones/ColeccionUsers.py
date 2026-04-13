from .Coleccion import Coleccion


class ColeccionUsers(Coleccion):
    NOMBRE_COLECCION = "users"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": ["email", "role", "status", "created_at"],
            "properties": {
                "email": {"bsonType": "string"},
                "role": {"enum": ["admin", "manager", "reader"]},
                "status": {"enum": ["pending_verification", "active", "disabled"]},
                "created_at": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "email", unique=True, name="idx_users_email_unique"
        )
