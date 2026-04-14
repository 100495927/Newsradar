COLLECTION_SPECS = [
    {
        "name": "rss_fuentes",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "hash_fuente",
                    "medio",
                    "url",
                    "activo",
                    "creado",
                    "actualizado",
                ],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "hash_fuente": {"bsonType": "string"},
                    "medio": {"bsonType": "string"},
                    "rss": {"bsonType": ["string", "null"]},
                    "url": {"bsonType": "string"},
                    "parser_id": {"bsonType": ["string", "null"]},
                    "activo": {"bsonType": "bool"},
                    "creado": {"bsonType": "date"},
                    "actualizado": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            {
                "keys": [("hash_fuente", 1)],
                "kwargs": {
                    "unique": True,
                    "name": "idx_rss_fuentes_hash_fuente_unique",
                },
            },
            {
                "keys": [("url", 1)],
                "kwargs": {"unique": True, "name": "idx_rss_fuentes_url_unique"},
            },
            {
                "keys": [("medio", 1), ("rss", 1)],
                "kwargs": {"name": "idx_rss_fuentes_medio_rss"},
            },
            {"keys": [("activo", 1)], "kwargs": {"name": "idx_rss_fuentes_activo"}},
        ],
    },
    {
        "name": "rss_entradas",
        "validator": {
            "$jsonSchema": {
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
                    "meta": {"bsonType": ["object", "null"]},
                },
            }
        },
        "indexes": [
            {
                "keys": [("hash_deduplicado", 1)],
                "kwargs": {
                    "unique": True,
                    "name": "idx_rss_entradas_hash_deduplicado_unique",
                },
            },
            {
                "keys": [("id_fuente", 1), ("fecha_publicacion", -1)],
                "kwargs": {"name": "idx_rss_entradas_fuente_fecha"},
            },
            {
                "keys": [("fecha_publicacion", -1)],
                "kwargs": {"name": "idx_rss_entradas_fecha_publicacion"},
            },
            {
                "keys": [("categorias", 1)],
                "kwargs": {"name": "idx_rss_entradas_categorias"},
            },
        ],
    },
    {
        "name": "rss_entradas_raw",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id_entrada", "id_fuente", "payload_raw", "fecha_captura"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "id_entrada": {"bsonType": "objectId"},
                    "id_fuente": {"bsonType": "objectId"},
                    "payload_raw": {"bsonType": "string"},
                    "formato_payload": {"bsonType": ["string", "null"]},
                    "fecha_captura": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            {
                "keys": [("id_entrada", 1)],
                "kwargs": {
                    "unique": True,
                    "name": "idx_rss_entradas_raw_id_entrada_unique",
                },
            },
            {
                "keys": [("id_fuente", 1), ("fecha_captura", -1)],
                "kwargs": {"name": "idx_rss_entradas_raw_fuente_fecha"},
            },
        ],
    },
    {
        "name": "users",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "email",
                    "first_name",
                    "last_name",
                    "organization",
                    "role",
                    "status",
                    "created_at",
                    "updated_at",
                ],
                "properties": {
                    "first_name": {"bsonType": "string"},
                    "last_name": {"bsonType": "string"},
                    "organization": {"bsonType": ["string", "null"]},
                    "email": {"bsonType": "string"},
                    "role": {"enum": ["admin", "manager", "reader"]},
                    "status": {"enum": ["pending_verification", "active", "disabled"]},
                    "password_hash": {"bsonType": ["string", "null"]},
                    "email_verified_at": {"bsonType": ["date", "null"]},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            {
                "keys": [("email", 1)],
                "kwargs": {"unique": True, "name": "idx_users_email_unique"},
            },
            {
                "keys": [("role", 1), ("status", 1)],
                "kwargs": {"name": "idx_users_role_status"},
            },
        ],
    },
    {
        "name": "user_sessions",
        "validator": {
            "$jsonSchema": {
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
        },
        "indexes": [
            {
                "keys": [("jti", 1)],
                "kwargs": {"unique": True, "name": "idx_user_sessions_jti_unique"},
            },
            {
                "keys": [("user_id", 1), ("token_type", 1), ("status", 1)],
                "kwargs": {"name": "idx_user_sessions_user_type_status"},
            },
            {
                "keys": [("expires_at", 1)],
                "kwargs": {
                    "expireAfterSeconds": 0,
                    "name": "idx_user_sessions_expires_ttl",
                },
            },
        ],
    },
]

EXPECTED_COLLECTION_NAMES = [spec["name"] for spec in COLLECTION_SPECS]
EXPECTED_INDEX_NAMES = {
    spec["name"]: [index["kwargs"]["name"] for index in spec["indexes"]]
    for spec in COLLECTION_SPECS
}

RUNTIME_REQUIRED_COLLECTIONS = [
    "rss_fuentes",
    "rss_entradas",
    "users",
    "user_sessions",
]

RUNTIME_REQUIRED_INDEXES = {
    "rss_fuentes": [
        "idx_rss_fuentes_hash_fuente_unique",
        "idx_rss_fuentes_url_unique",
    ],
    "rss_entradas": [
        "idx_rss_entradas_hash_deduplicado_unique",
        "idx_rss_entradas_fuente_fecha",
    ],
    "users": [
        "idx_users_email_unique",
    ],
    "user_sessions": [
        "idx_user_sessions_jti_unique",
        "idx_user_sessions_user_type_status",
        "idx_user_sessions_expires_ttl",
    ],
}

__all__ = [
    "COLLECTION_SPECS",
    "EXPECTED_COLLECTION_NAMES",
    "EXPECTED_INDEX_NAMES",
    "RUNTIME_REQUIRED_COLLECTIONS",
    "RUNTIME_REQUIRED_INDEXES",
]
