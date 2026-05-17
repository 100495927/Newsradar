from __future__ import annotations


def _index(keys: dict, **kwargs) -> dict:
    return {"keys": list(keys.items()), "kwargs": kwargs}


COLLECTION_SPECS = [
    {
        "name": "information_sources",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "name", "url", "active", "created_at", "updated_at"],
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
        },
        "indexes": [
            _index({"id": 1}, unique=True, name="idx_information_sources_id_unique"),
            _index(
                {"url": 1},
                unique=True,
                partialFilterExpression={"deleted_at": None},
                name="idx_information_sources_url_unique_active",
            ),
            _index({"active": 1, "name": 1}, name="idx_information_sources_active_name"),
        ],
    },
    {
        "name": "rss_channels",
        "validator": {
            "$jsonSchema": {
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
        },
        "indexes": [
            _index({"id": 1}, unique=True, name="idx_rss_channels_id_unique"),
            _index(
                {"url": 1},
                unique=True,
                partialFilterExpression={"deleted_at": None},
                name="idx_rss_channels_url_unique_active",
            ),
            _index(
                {"information_source_id": 1, "active": 1},
                name="idx_rss_channels_source_active",
            ),
            _index({"category_id": 1, "active": 1}, name="idx_rss_channels_category_active"),
        ],
    },
    {
        "name": "rss_entradas",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "information_source_id",
                    "rss_channel_id",
                    "titulo",
                    "autores",
                    "link",
                    "fecha_publicacion",
                    "hash_deduplicado",
                    "fecha_ingestion",
                ],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "information_source_id": {"bsonType": ["int", "long"]},
                    "rss_channel_id": {"bsonType": ["int", "long"]},
                    "source_name": {"bsonType": ["string", "null"]},
                    "source_url": {"bsonType": ["string", "null"]},
                    "channel_url": {"bsonType": ["string", "null"]},
                    "titulo": {"bsonType": "string"},
                    "autores": {"bsonType": ["array", "null"]},
                    "link": {"bsonType": "string"},
                    "category_id": {"bsonType": ["int", "null"]},
                    "resumen": {"bsonType": ["string", "null"]},
                    "fecha_publicacion": {"bsonType": "date"},
                    "hash_deduplicado": {"bsonType": "string"},
                    "fecha_ingestion": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            _index(
                {"hash_deduplicado": 1},
                unique=True,
                name="idx_rss_entradas_hash_deduplicado_unique",
            ),
            _index({"rss_channel_id": 1, "fecha_publicacion": -1}, name="idx_rss_entradas_channel_fecha"),
            _index(
                {"information_source_id": 1, "fecha_publicacion": -1},
                name="idx_rss_entradas_source_fecha",
            ),
            _index({"fecha_publicacion": -1}, name="idx_rss_entradas_fecha_publicacion"),
            _index({"category_id": 1}, name="idx_rss_entradas_category_id"),
        ],
    },
    {
        "name": "rss_categorias_iptc",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["_id", "descripciones"],
                "properties": {
                    "_id": {
                        "bsonType": "int",
                        "description": "IPTC Subject NewsCode (Primary Key)",
                    },
                    "id_padre": {
                        "bsonType": ["int", "null"],
                        "description": "ID of the parent category",
                    },
                    "nivel": {
                        "bsonType": ["int", "null"],
                        "description": "Hierarchical depth level",
                    },
                    "descripciones": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["idioma", "nombre"],
                            "properties": {
                                "idioma": {"bsonType": "string"},
                                "nombre": {"bsonType": "string"},
                                "descripcion": {"bsonType": "string"},
                            },
                        },
                    },
                    "subcategorias": {
                        "bsonType": "array",
                        "items": {"bsonType": "int"},
                        "description": "List of child category IDs",
                    },
                },
            }
        },
        "indexes": [
            _index({"id_padre": 1}, name="idx_rss_categorias_iptc_id_padre"),
            _index({"descripciones.nombre": "text"}, name="idx_rss_categorias_iptc_nombre_text"),
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
                    "email": {"bsonType": "string"},
                    "first_name": {"bsonType": "string"},
                    "last_name": {"bsonType": "string"},
                    "organization": {"bsonType": ["string", "null"]},
                    "role": {"enum": ["gestor", "reader"]},
                    "status": {"enum": ["pending_verification", "active", "disabled"]},
                    "password_hash": {"bsonType": ["string", "null"]},
                    "email_verified_at": {"bsonType": ["date", "null"]},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            _index({"email": 1}, unique=True, name="idx_users_email_unique"),
            _index({"role": 1, "status": 1}, name="idx_users_role_status"),
        ],
    },
    {
        "name": "user_sessions",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "jti", "token_type", "issued_at", "expires_at", "status"],
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
            _index({"jti": 1}, unique=True, name="idx_user_sessions_jti_unique"),
            _index(
                {"user_id": 1, "token_type": 1, "status": 1},
                name="idx_user_sessions_user_type_status",
            ),
            _index({"expires_at": 1}, expireAfterSeconds=0, name="idx_user_sessions_expires_ttl"),
        ],
    },
    {
        "name": "alerts",
        "validator": {
            "$jsonSchema": {
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
        },
        "indexes": [
            _index({"id": 1}, unique=True, name="idx_alerts_id_unique"),
            _index({"user_id": 1, "enabled": 1, "next_run_at": 1}, name="idx_alerts_user_enabled_next_run"),
            _index({"category_id": 1, "enabled": 1}, name="idx_alerts_category_enabled"),
            _index({"rss_channel_ids": 1}, name="idx_alerts_rss_channel_ids"),
            _index(
                {"information_sources_ids": 1},
                name="idx_alerts_information_sources_ids",
            ),
        ],
    },
    {
        "name": "notifications",
        "validator": {
            "$jsonSchema": {
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
        },
        "indexes": [
            _index({"id": 1}, unique=True, name="idx_notifications_id_unique"),
            _index({"alert_id": 1, "timestamp": -1}, name="idx_notifications_alert_timestamp"),
            _index(
                {"user_id": 1, "read_at": 1, "timestamp": -1},
                name="idx_notifications_user_read_timestamp",
            ),
            _index({"email_status": 1, "created_at": 1}, name="idx_notifications_email_status_created"),
        ],
    },
    {
        "name": "stats",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "metrics"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "id": {"bsonType": ["int", "long"]},
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
                },
            }
        },
        "indexes": [_index({"id": 1}, unique=True, name="idx_stats_id_unique")],
    },
    {
        "name": "counters",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["_id", "seq", "updated_at"],
                "properties": {
                    "_id": {"bsonType": "string"},
                    "seq": {"bsonType": ["int", "long"]},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "indexes": [],
    },
]


COUNTER_SEEDS = [
    {"_id": "information_sources", "seq": 0},
    {"_id": "rss_channels", "seq": 0},
    {"_id": "users", "seq": 0},
    {"_id": "alerts", "seq": 0},
    {"_id": "notifications", "seq": 0},
]


__all__ = ["COLLECTION_SPECS", "COUNTER_SEEDS"]
