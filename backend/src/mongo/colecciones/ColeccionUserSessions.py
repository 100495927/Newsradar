from .Coleccion import Coleccion


class ColeccionUserSessions(Coleccion):
    NOMBRE_COLECCION = "user_sessions"

    def esquema(self) -> dict:
        return {
            "bsonType": "object",
            "required": [
                "user_id",
                "jti",
                "token_type",
                "issued_at",
                "expires_at",
                "status",
            ],
            "properties": {
                "user_id": {"bsonType": "objectId"},
                "jti": {"bsonType": "string"},
                "token_type": {"enum": ["access", "refresh"]},
                "status": {"enum": ["active", "revoked", "expired"]},
                "issued_at": {"bsonType": "date"},
                "expires_at": {"bsonType": "date"},
                "revoked_at": {"bsonType": ["date", "null"]},
                "revoke_reason": {"bsonType": ["string", "null"]},
                "user_agent": {"bsonType": ["string", "null"]},
                "ip": {"bsonType": ["string", "null"]},
                "created_at": {"bsonType": ["date", "null"]},
            },
        }

    def crear_indices(self):
        # El JTI (JSON Token Identifier) debe ser único para prevenir Replay Attacks
        self._collection.create_index(
            "jti", unique=True, name="idx_user_sessions_jti_unique"
        )
        # Optimiza la búsqueda de sesiones activas por usuario
        self._collection.create_index(
            [("user_id", 1), ("token_type", 1), ("status", 1)],
            name="idx_user_sessions_user_type_status",
        )

        # ÍNDICE TTL: Borra automáticamente el documento cuando llega a 'expires_at'
        # expireAfterSeconds=0 significa que expira exactamente en la fecha del campo
        self._collection.create_index(
            "expires_at", expireAfterSeconds=0, name="idx_user_sessions_expires_ttl"
        )
