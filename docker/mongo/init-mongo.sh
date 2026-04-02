#!/bin/bash
# Bootstrap inicial de MongoDB para NewsRadar.
# Resultado esperado: usuario de aplicacion, colecciones RSS/usuarios y sus indices
# quedan creados al primer arranque cuando /data/db esta vacio.
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

ensureCollection("rss_fuentes", {
  $jsonSchema: {
    bsonType: "object",
    required: ["hash_fuente", "medio", "url", "activo", "creado", "actualizado"],
    properties: {
      _id: { bsonType: "objectId" },
      hash_fuente: { bsonType: "string" },
      medio: { bsonType: "string" },
      rss: { bsonType: ["string", "null"] },
      url: { bsonType: "string" },
      parser_id: { bsonType: ["string", "null"] },
      activo: { bsonType: "bool" },
      creado: { bsonType: "date" },
      actualizado: { bsonType: "date" }
    }
  }
});

ensureCollection("rss_entradas", {
  $jsonSchema: {
    bsonType: "object",
    required: ["id_fuente", "titulo", "autores", "link", "fecha_publicacion", "hash_deduplicado", "fecha_ingestion"],
    properties: {
      _id: { bsonType: "objectId" },
      id_fuente: { bsonType: "objectId" },
      titulo: { bsonType: "string" },
      link: { bsonType: "string" },
      resumen: { bsonType: ["string", "null"] },
      autores: { bsonType: ["array", "null"] },
      categorias: { bsonType: ["array", "null"] },
      fecha_publicacion: { bsonType: "date" },
      hash_deduplicado: { bsonType: "string" },
      fecha_ingestion: { bsonType: "date" },
      meta: { bsonType: ["object", "null"] }
    }
  }
});

ensureCollection("rss_entradas_raw", {
  $jsonSchema: {
    bsonType: "object",
    required: ["id_entrada", "id_fuente", "payload_raw", "fecha_captura"],
    properties: {
      _id: { bsonType: "objectId" },
      id_entrada: { bsonType: "objectId" },
      id_fuente: { bsonType: "objectId" },
      payload_raw: { bsonType: "string" },
      formato_payload: { bsonType: ["string", "null"] },
      fecha_captura: { bsonType: "date" }
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

db.rss_fuentes.createIndex({ hash_fuente: 1 }, { unique: true, name: "idx_rss_fuentes_hash_fuente_unique" });
db.rss_fuentes.createIndex({ url: 1 }, { unique: true, name: "idx_rss_fuentes_url_unique" });
db.rss_fuentes.createIndex({ medio: 1, rss: 1 }, { name: "idx_rss_fuentes_medio_rss" });
db.rss_fuentes.createIndex({ activo: 1 }, { name: "idx_rss_fuentes_activo" });

db.rss_entradas.createIndex({ hash_deduplicado: 1 }, { unique: true, name: "idx_rss_entradas_hash_deduplicado_unique" });
db.rss_entradas.createIndex({ id_fuente: 1, fecha_publicacion: -1 }, { name: "idx_rss_entradas_fuente_fecha" });
db.rss_entradas.createIndex({ fecha_publicacion: -1 }, { name: "idx_rss_entradas_fecha_publicacion" });
db.rss_entradas.createIndex({ categorias: 1 }, { name: "idx_rss_entradas_categorias" });

db.rss_entradas_raw.createIndex({ id_entrada: 1 }, { unique: true, name: "idx_rss_entradas_raw_id_entrada_unique" });
db.rss_entradas_raw.createIndex({ id_fuente: 1, fecha_captura: -1 }, { name: "idx_rss_entradas_raw_fuente_fecha" });

db.users.createIndex({ email: 1 }, { unique: true, name: "idx_users_email_unique" });
db.users.createIndex({ role: 1, status: 1 }, { name: "idx_users_role_status" });

db.user_sessions.createIndex({ jti: 1 }, { unique: true, name: "idx_user_sessions_jti_unique" });
db.user_sessions.createIndex({ user_id: 1, token_type: 1, status: 1 }, { name: "idx_user_sessions_user_type_status" });
db.user_sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0, name: "idx_user_sessions_expires_ttl" });

print("[init-mongo] Inicializacion de colecciones e indices completada");
EOF
