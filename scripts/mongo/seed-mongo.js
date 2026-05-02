db = db.getSiblingDB(process.env.MONGO_APP_DB);
const crypto = require("crypto");

const POLITICS = 11000000;
const SPORT = 15000000;
const SOCIETY = 14000000;

const DEFAULT_ADMIN_EMAIL = process.env.NEWSRADAR_ADMIN_EMAIL || "AdminDefault@newsradar.com";
const DEFAULT_ADMIN_PASSWORD_HASH =
  process.env.NEWSRADAR_ADMIN_PASSWORD_HASH ||
  "$2b$12$0ToWA9DEv0ZllCHPqxXtKev5L2au/M4VvXVMX5MBp/ydq79CfdBBC";

const IPTC_TOP_LEVEL_CATEGORIES = [
  { id: 1000000, name: "Artes, cultura, entretenimiento y medios" },
  { id: 3000000, name: "Catástrofes y accidentes" },
  { id: 13000000, name: "Ciencia y tecnología" },
  { id: 16000000, name: "Conflicto, guerra y paz" },
  { id: 15000000, name: "Deporte" },
  { id: 4000000, name: "Economía, negocios y finanzas" },
  { id: 5000000, name: "Educación" },
  { id: 10000000, name: "Estilo de vida y tiempo libre" },
  { id: 8000000, name: "Interés humano, animales, insólito" },
  { id: 9000000, name: "Mano de obra" },
  { id: 6000000, name: "Medio ambiente" },
  { id: 17000000, name: "Meteorología" },
  { id: 2000000, name: "Policía y justicia" },
  { id: 11000000, name: "Política" },
  { id: 12000000, name: "Religión y culto" },
  { id: 7000000, name: "Salud" },
  { id: 14000000, name: "Sociedad" },
];

const STANDARD_RSS_SOURCES = [
  { medio: "el_pais", rss: "portada", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", category_id: SOCIETY },
  { medio: "el_pais", rss: "america", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/america/portada", category_id: POLITICS },
  { medio: "el_pais", rss: "english", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/english.elpais.com/portada", category_id: SOCIETY },
  { medio: "el_pais", rss: "mexico", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/mexico/portada", category_id: POLITICS },
  { medio: "el_pais", rss: "colombia", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/america-colombia/portada", category_id: POLITICS },
  { medio: "el_pais", rss: "chile", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/chile/portada", category_id: POLITICS },
  { medio: "el_pais", rss: "argentina", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/argentina/portada", category_id: POLITICS },
  { medio: "abcnews", rss: "us", url: "https://abcnews.com/abcnews/usheadlines", category_id: SOCIETY },
  { medio: "abcnews", rss: "international", url: "https://abcnews.com/abcnews/internationalheadlines", category_id: POLITICS },
  { medio: "abcnews", rss: "politics", url: "https://abcnews.com/abcnews/politicsheadlines", category_id: POLITICS },
  { medio: "abc", rss: "", url: "https://www.abc.es/rss/feeds/abcPortada.xml", category_id: SOCIETY },
  { medio: "bbc", rss: "mundo", url: "https://feeds.bbci.co.uk/news/world/rss.xml", category_id: POLITICS },
  { medio: "rtve", rss: "noticias", url: "https://api2.rtve.es/rss/temas_noticias.xml", category_id: SOCIETY },
  { medio: "elconfidencial", rss: "mundo", url: "https://rss.elconfidencial.com/mundo/", category_id: POLITICS },
  { medio: "marca", rss: "primera_division", url: "https://objetos.estaticos-marca.com/rss/futbol/primera-division.xml", category_id: SPORT },
  { medio: "marca", rss: "segunda_division", url: "https://objetos.estaticos-marca.com/rss/futbol/segunda-division.xml", category_id: SPORT },
  { medio: "marca", rss: "mas_futbol", url: "https://objetos.estaticos-marca.com/rss/futbol/mas-futbol.xml", category_id: SPORT },
  { medio: "marca", rss: "copa_del_rey", url: "https://objetos.estaticos-marca.com/rss/futbol/copa-rey.xml", category_id: SPORT },
  { medio: "marca", rss: "furbol_femenino", url: "https://objetos.estaticos-marca.com/rss/futbol/futbol-femenino.xml", category_id: SPORT },
  { medio: "marca", rss: "seleccion_española", url: "https://objetos.estaticos-marca.com/rss/futbol/seleccion.xml", category_id: SPORT },
  { medio: "marca", rss: "futbol_sala", url: "https://objetos.estaticos-marca.com/rss/futbol/futbol-sala.xml", category_id: SPORT },
  { medio: "marca", rss: "futbol_internacional", url: "https://objetos.estaticos-marca.com/rss/futbol/futbol-internacional.xml", category_id: SPORT },
  { medio: "marca", rss: "champions_league", url: "https://objetos.estaticos-marca.com/rss/futbol/champions-league.xml", category_id: SPORT },
  { medio: "marca", rss: "europa_league", url: "https://objetos.estaticos-marca.com/rss/futbol/europa-league.xml", category_id: SPORT },
  { medio: "marca", rss: "premier_league", url: "https://objetos.estaticos-marca.com/rss/futbol/premier-league.xml", category_id: SPORT },
  { medio: "marca", rss: "bundersliga", url: "https://objetos.estaticos-marca.com/rss/futbol/bundesliga.xml", category_id: SPORT },
  { medio: "marca", rss: "liga_italiana", url: "https://objetos.estaticos-marca.com/rss/futbol/liga-italiana.xml", category_id: SPORT },
  { medio: "marca", rss: "liga_francesa", url: "https://objetos.estaticos-marca.com/rss/futbol/liga-francesa.xml", category_id: SPORT },
  { medio: "marca", rss: "mundial_de_clubes", url: "https://objetos.estaticos-marca.com/rss/futbol/mundial-de-clubes.xml", category_id: SPORT },
  { medio: "marca", rss: "america", url: "https://objetos.estaticos-marca.com/rss/futbol/america.xml", category_id: SPORT },
  { medio: "esdiario", rss: "", url: "https://www.esdiario.com/rss/home.xml", category_id: SOCIETY },
  { medio: "antena3", rss: "", url: "https://www.antena3.com/noticias/rss/4013050.xml", category_id: SOCIETY },
  { medio: "ministerio_dsa", rss: "", url: "https://www.dsca.gob.es/es/rss-noticias.xml", category_id: POLITICS },
  { medio: "moncloa", rss: "", url: "https://www.lamoncloa.gob.es/paginas/rss.aspx", category_id: POLITICS },
];

function hashFuente(medio, rss) {
  return crypto.createHash("sha256").update(`${medio}${rss || ""}`, "utf8").digest("hex");
}

function ensureUsersCounterAtLeast(seedValue) {
  db.getCollection("counters").updateOne(
    { _id: "users" },
    {
      $max: { seq: NumberInt(seedValue) },
      $set: { updated_at: new Date() },
    },
    { upsert: true }
  );
}

function seedIptcCategories() {
  const collection = db.getCollection("rss_categorias_iptc");
  IPTC_TOP_LEVEL_CATEGORIES.forEach((category) => {
    collection.updateOne(
      { _id: NumberInt(category.id) },
      {
        $set: {
          id_padre: null,
          nivel: NumberInt(1),
          descripciones: [
            {
              idioma: "es",
              nombre: category.name,
              descripcion: category.name,
            },
          ],
          subcategorias: [],
        },
      },
      { upsert: true }
    );
  });
  print("[seed-mongo] Categorias IPTC reconciliadas: " + IPTC_TOP_LEVEL_CATEGORIES.length);
}

function seedAdminUser() {
  const users = db.getCollection("users");
  const now = new Date();
  const existing = users.findOne({
    $or: [
      { id: NumberInt(1) },
      { email: DEFAULT_ADMIN_EMAIL },
      { email: "AdminDefault@newsradar.local" },
    ],
  });

  const adminDoc = {
    id: NumberInt(1),
    email: DEFAULT_ADMIN_EMAIL,
    first_name: "AdminDefault",
    last_name: "NewsRadar",
    organization: "NewsRadar",
    role_ids: [NumberInt(1)],
    role: "manager",
    status: "active",
    password_hash: DEFAULT_ADMIN_PASSWORD_HASH,
    is_verified: true,
    email_verified_at: now,
    updated_at: now,
  };

  if (existing) {
    users.updateOne(
      { _id: existing._id },
      {
        $set: {
          ...adminDoc,
          created_at: existing.created_at || now,
        },
      }
    );
    print("[seed-mongo] Usuario admin actualizado: " + DEFAULT_ADMIN_EMAIL);
  } else {
    users.insertOne({
      ...adminDoc,
      created_at: now,
    });
    print("[seed-mongo] Usuario admin creado: " + DEFAULT_ADMIN_EMAIL);
  }

  ensureUsersCounterAtLeast(1);
}

function seedStandardRssSources() {
  const collection = db.getCollection("rss_fuentes");
  const now = new Date();

  STANDARD_RSS_SOURCES.forEach((source) => {
    const hash = hashFuente(source.medio, source.rss);
    collection.updateOne(
      { hash_fuente: hash },
      {
        $set: {
          hash_fuente: hash,
          medio: source.medio,
          rss: source.rss,
          url: source.url,
          tipo: "channel",
          activo: true,
          category_id: NumberInt(source.category_id),
          actualizado: now,
        },
        $setOnInsert: {
          creado: now,
        },
      },
      { upsert: true }
    );
  });

  print("[seed-mongo] Fuentes RSS base reconciliadas: " + STANDARD_RSS_SOURCES.length);
}

seedIptcCategories();
seedAdminUser();
seedStandardRssSources();

print("[seed-mongo] Semilla inicial aplicada correctamente");
