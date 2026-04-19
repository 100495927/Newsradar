db = db.getSiblingDB(process.env.MONGO_APP_DB);

const appUser = process.env.MONGO_APP_USER;
const appPassword = process.env.MONGO_APP_PASSWORD;
const appDbName = process.env.MONGO_APP_DB;

function ensureAppUser() {
  const userInfo = db.getUser(appUser);
  if (!userInfo) {
    db.createUser({
      user: appUser,
      pwd: appPassword,
      roles: [{ role: "readWrite", db: appDbName }],
    });
    print("[init-mongo] Usuario de aplicacion creado");
    return;
  }

  db.updateUser(appUser, {
    pwd: appPassword,
    roles: [{ role: "readWrite", db: appDbName }],
  });
  print("[init-mongo] Usuario de aplicacion actualizado");
}

function ensureCollection(name, validator) {
  const exists = db.getCollectionInfos({ name }).length > 0;
  if (!exists) {
    db.createCollection(name, {
      validator,
      validationLevel: "moderate",
    });
    print("[init-mongo] Coleccion creada: " + name);
    return;
  }

  db.runCommand({
    collMod: name,
    validator,
    validationLevel: "moderate",
  });
  print("[init-mongo] Coleccion actualizada: " + name);
}

function ensureIndexes(name, indexes) {
  const collection = db.getCollection(name);
  indexes.forEach((indexSpec) => {
    collection.createIndex(indexSpec.keys, indexSpec.options);
    print("[init-mongo] Indice asegurado: " + name + "." + indexSpec.options.name);
  });
}

ensureAppUser();

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
      activo: { bsonType: "bool" },
      categoria_iptc: { bsonType: ["string", "null"] },
      creado: { bsonType: "date" },
      actualizado: { bsonType: "date" },
    },
  },
});
ensureIndexes("rss_fuentes", [
  {
    keys: { hash_fuente: 1 },
    options: { unique: true, name: "idx_rss_fuentes_hash_fuente_unique" },
  },
  {
    keys: { url: 1 },
    options: { unique: true, name: "idx_rss_fuentes_url_unique" },
  },
  {
    keys: { medio: 1, rss: 1 },
    options: { name: "idx_rss_fuentes_medio_rss" },
  },
  {
    keys: { activo: 1 },
    options: { name: "idx_rss_fuentes_activo" },
  },
]);

ensureCollection("rss_entradas", {
  $jsonSchema: {
    bsonType: "object",
    required: [
      "id_fuente",
      "titulo",
      "autores",
      "link",
      "fecha_publicacion",
      "hash_deduplicado",
      "fecha_ingestion",
    ],
    properties: {
      _id: { bsonType: "objectId" },
      id_fuente: { bsonType: "objectId" },
      titulo: { bsonType: "string" },
      autores: { bsonType: ["array", "null"] },
      link: { bsonType: "string" },
      categorias: { bsonType: ["array", "null"] },
      categorias_raw: { bsonType: ["array", "null"] },
      resumen: { bsonType: ["string", "null"] },
      fecha_publicacion: { bsonType: "date" },
      hash_deduplicado: { bsonType: "string" },
      fecha_ingestion: { bsonType: "date" },
    },
  },
});
*** Add File: rss-worker/tests/rss/test_iptc.py
from rss.iptc import canonicalize_iptc_category, normalize_feed_categories
from rss.parsers.RSSParser import RSSParser
from rss.RSSFuente import RSSFuente


class DummyTag:
    def __init__(self, term: str):
        self.term = term


class DummyEntry(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc


def test_canonicalize_exact_iptc_category() -> None:
    assert canonicalize_iptc_category("Política") == "Política"


def test_canonicalize_alias_to_top_level() -> None:
    assert canonicalize_iptc_category("Phishing") == "Ciencia y tecnología"


def test_normalize_feed_categories_uses_fallback_when_raw_tags_are_not_iptc() -> None:
    categorias, categorias_raw = normalize_feed_categories(
        ["General"],
        "Política",
    )

    assert categorias == ["Política"]
    assert categorias_raw == ["General"]


def test_parser_stores_raw_categories_and_normalized_iptc_categories() -> None:
    entry = DummyEntry(
        title="Titulo",
        link="https://example.com/noticia",
        summary="Resumen",
        published_parsed=(2026, 4, 19, 12, 0, 0, 0, 0, 0),
        tags=[DummyTag("Phishing"), DummyTag("General")],
    )
    parser = RSSParser(entry)
    fuente = RSSFuente(
        "hispasec",
        "una_al_dia",
        "https://feeds.feedburner.com/hispasec/zCAd",
        categoria_iptc="Ciencia y tecnología",
    )

    noticia = parser.generar(fuente)

    assert noticia.categorias == ["Ciencia y tecnología"]
    assert noticia.categorias_raw == ["Phishing", "General"]
ensureIndexes("rss_entradas", [
  {
    keys: { hash_deduplicado: 1 },
    options: { unique: true, name: "idx_rss_entradas_hash_deduplicado_unique" },
  },
  {
    keys: { id_fuente: 1, fecha_publicacion: -1 },
    options: { name: "idx_rss_entradas_fuente_fecha" },
  },
  {
    keys: { fecha_publicacion: -1 },
    options: { name: "idx_rss_entradas_fecha_publicacion" },
  },
  {
    keys: { categorias: 1 },
    options: { name: "idx_rss_entradas_categorias" },
  },
]);

ensureCollection("users", {
  $jsonSchema: {
    bsonType: "object",
    required: [
      "email",
      "first_name",
      "last_name",
      "organization",
      "role",
      "status",
      "created_at",
      "updated_at",
    ],
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
      updated_at: { bsonType: "date" },
    },
  },
});
ensureIndexes("users", [
  {
    keys: { email: 1 },
    options: { unique: true, name: "idx_users_email_unique" },
  },
  {
    keys: { role: 1, status: 1 },
    options: { name: "idx_users_role_status" },
  },
]);

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
      created_at: { bsonType: ["date", "null"] },
    },
  },
});
ensureIndexes("user_sessions", [
  {
    keys: { jti: 1 },
    options: { unique: true, name: "idx_user_sessions_jti_unique" },
  },
  {
    keys: { user_id: 1, token_type: 1, status: 1 },
    options: { name: "idx_user_sessions_user_type_status" },
  },
  {
    keys: { expires_at: 1 },
    options: { expireAfterSeconds: 0, name: "idx_user_sessions_expires_ttl" },
  },
]);

print("[init-mongo] Inicializacion de colecciones e indices completada");
