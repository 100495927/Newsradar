#!/bin/bash
set -euo pipefail

if [ -z "${MONGO_APP_USER:-}" ] || [ -z "${MONGO_APP_PASSWORD:-}" ] || [ -z "${MONGO_APP_DB:-}" ]; then
  echo "[init-mongo] Faltan variables MONGO_APP_USER, MONGO_APP_PASSWORD o MONGO_APP_DB" >&2
  exit 1
fi

mongosh --authenticationDatabase "$MONGO_INITDB_DATABASE" \
  -u "$MONGO_INITDB_ROOT_USERNAME" \
  -p "$MONGO_INITDB_ROOT_PASSWORD" <<EOF
use $MONGO_APP_DB

if (!db.getUser("$MONGO_APP_USER")) {
  db.createUser({
    user: "$MONGO_APP_USER",
    pwd: "$MONGO_APP_PASSWORD",
    roles: [{ role: "readWrite", db: "$MONGO_APP_DB" }]
  });
  print("[init-mongo] Usuario de aplicacion creado");
} else {
  print("[init-mongo] Usuario de aplicacion ya existe");
}

function ensureCollection(name, validator) {
  const exists = db.getCollectionInfos({ name: name }).length > 0;
  if (!exists) {
    db.createCollection(name, {
      validator: validator,
      validationLevel: "moderate"
    });
    print("[init-mongo] Coleccion creada: " + name);
  } else {
    print("[init-mongo] Coleccion ya existe: " + name);
  }
}

ensureCollection("rss_sources", {
  $jsonSchema: {
    bsonType: "object",
    required: ["medio", "url", "active", "created_at", "updated_at"],
    properties: {
      medio: { bsonType: "string" },
      rss: { bsonType: ["string", "null"] },
      url: { bsonType: "string" },
      parser_hint: { bsonType: ["string", "null"] },
      active: { bsonType: "bool" },
      created_at: { bsonType: "date" },
      updated_at: { bsonType: "date" }
    }
  }
});

ensureCollection("rss_items", {
  $jsonSchema: {
    bsonType: "object",
    required: ["source_id", "title", "link", "published_at", "dedup_key", "ingested_at"],
    properties: {
      source_id: { bsonType: "objectId" },
      title: { bsonType: "string" },
      link: { bsonType: "string" },
      summary: { bsonType: ["string", "null"] },
      authors: { bsonType: ["array", "null"] },
      categories: { bsonType: ["array", "null"] },
      published_at: { bsonType: "date" },
      dedup_key: { bsonType: "string" },
      ingested_at: { bsonType: "date" },
      updated_at: { bsonType: ["date", "null"] },
      meta: { bsonType: ["object", "null"] }
    }
  }
});

ensureCollection("rss_items_raw", {
  $jsonSchema: {
    bsonType: "object",
    required: ["item_id", "source_id", "raw_payload", "captured_at"],
    properties: {
      item_id: { bsonType: "objectId" },
      source_id: { bsonType: "objectId" },
      raw_payload: { bsonType: "string" },
      payload_format: { bsonType: ["string", "null"] },
      captured_at: { bsonType: "date" }
    }
  }
});

ensureCollection("users", {
  $jsonSchema: {
    bsonType: "object",
    required: ["email", "first_name", "last_name", "organization", "role", "status", "created_at", "updated_at"],
    properties: {
      email: { bsonType: "string" },
      first_name: { bsonType: "string" },
      last_name: { bsonType: "string" },
      organization: { bsonType: ["string", "null"] },
      role: { enum: ["admin", "manager", "reader"] },
      status: { enum: ["pending_verification", "active", "disabled"] },
      password_hash: { bsonType: ["string", "null"] },
      email_verified_at: { bsonType: ["date", "null"] },
      created_at: { bsonType: "date" },
      updated_at: { bsonType: "date" }
    }
  }
});

// JWT future support only: persistence layer without auth endpoint implementation.
ensureCollection("user_sessions", {
  $jsonSchema: {
    bsonType: "object",
    required: ["user_id", "jti", "token_type", "issued_at", "expires_at", "status"],
    properties: {
      user_id: { bsonType: "objectId" },
      jti: { bsonType: "string" },
      token_type: { enum: ["access", "refresh"] },
      status: { enum: ["active", "revoked", "expired"] },
      issued_at: { bsonType: "date" },
      expires_at: { bsonType: "date" },
      revoked_at: { bsonType: ["date", "null"] },
      revoke_reason: { bsonType: ["string", "null"] },
      user_agent: { bsonType: ["string", "null"] },
      ip: { bsonType: ["string", "null"] },
      created_at: { bsonType: ["date", "null"] }
    }
  }
});

db.rss_sources.createIndex({ url: 1 }, { unique: true, name: "idx_rss_sources_url_unique" });
db.rss_sources.createIndex({ medio: 1, rss: 1 }, { name: "idx_rss_sources_medio_rss" });
db.rss_sources.createIndex({ active: 1 }, { name: "idx_rss_sources_active" });

db.rss_items.createIndex({ dedup_key: 1 }, { unique: true, name: "idx_rss_items_dedup_unique" });
db.rss_items.createIndex({ source_id: 1, published_at: -1 }, { name: "idx_rss_items_source_date" });
db.rss_items.createIndex({ published_at: -1 }, { name: "idx_rss_items_published_at" });
db.rss_items.createIndex({ categories: 1 }, { name: "idx_rss_items_categories" });

db.rss_items_raw.createIndex({ item_id: 1 }, { unique: true, name: "idx_rss_items_raw_item_unique" });
db.rss_items_raw.createIndex({ source_id: 1, captured_at: -1 }, { name: "idx_rss_items_raw_source_captured" });

db.users.createIndex({ email: 1 }, { unique: true, name: "idx_users_email_unique" });
db.users.createIndex({ role: 1, status: 1 }, { name: "idx_users_role_status" });

db.user_sessions.createIndex({ jti: 1 }, { unique: true, name: "idx_user_sessions_jti_unique" });
db.user_sessions.createIndex({ user_id: 1, token_type: 1, status: 1 }, { name: "idx_user_sessions_user_type_status" });
db.user_sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0, name: "idx_user_sessions_expires_ttl" });

print("[init-mongo] Inicializacion de colecciones e indices completada");
EOF
