db = db.getSiblingDB(process.env.MONGO_APP_DB);

const DEFAULT_ADMIN_EMAIL = process.env.NEWSRADAR_ADMIN_EMAIL || "admin@newsradar.com";
const DEFAULT_ADMIN_PASSWORD_HASH =
  process.env.NEWSRADAR_ADMIN_PASSWORD_HASH ||
  "$2b$12$uTKblh4KngynF/XGVsMYVe7rkzxjKS8e6DdMENj5RbFi1jmKKDsAS";

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
  { medio: "El País", rss: "Economía", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", category_id: 4000000 },
  { medio: "El País", rss: "Política", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional", category_id: 11000000 },
  { medio: "El País", rss: "Deporte", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/deportes", category_id: 15000000 },
  { medio: "El País", rss: "Cultura", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/cultura", category_id: 1000000 },
  { medio: "El País", rss: "Ciencia y tecnología", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia", category_id: 13000000 },
  { medio: "El Mundo", rss: "Política", url: "https://www.elmundo.es/rss/portada.xml", category_id: 11000000 },
  { medio: "El Mundo", rss: "Política 2", url: "https://www.elmundo.es/rss/espana.xml", category_id: 11000000 },
  { medio: "El Mundo", rss: "Economía", url: "https://www.elmundo.es/rss/economia.xml", category_id: 4000000 },
  { medio: "El Mundo", rss: "Salud", url: "https://www.elmundo.es/rss/ciencia-y-salud.xml", category_id: 7000000 },
  { medio: "El Mundo", rss: "Deporte", url: "https://www.elmundo.es/rss/deportes.xml", category_id: 15000000 },
  { medio: "ABC", rss: "Política", url: "https://www.abc.es/rss/2.0/portada/", category_id: 11000000 },
  { medio: "ABC", rss: "Diplomacia", url: "https://www.abc.es/rss/2.0/internacional/", category_id: 11000000 },
  { medio: "ABC", rss: "Asuntos sociales", url: "https://www.abc.es/rss/2.0/sociedad/", category_id: 14000000 },
  { medio: "ABC", rss: "Cultura", url: "https://www.abc.es/rss/2.0/cultura/", category_id: 1000000 },
  { medio: "ABC", rss: "Ciencia y tecnología", url: "https://www.abc.es/rss/2.0/ciencia/", category_id: 13000000 },
  { medio: "RTVE", rss: "Política", url: "https://www.rtve.es/noticias/rss/noticias.xml", category_id: 11000000 },
  { medio: "RTVE", rss: "Diplomacia", url: "https://www.rtve.es/noticias/rss/mundo.xml", category_id: 11000000 },
  { medio: "RTVE", rss: "Ciencia y tecnología", url: "https://www.rtve.es/noticias/rss/tecnologia.xml", category_id: 13000000 },
  { medio: "RTVE", rss: "Cultura", url: "https://www.rtve.es/noticias/rss/cultura.xml", category_id: 1000000 },
  { medio: "RTVE", rss: "Deporte", url: "https://www.rtve.es/noticias/rss/deportes.xml", category_id: 15000000 },
  { medio: "Xataka", rss: "Ciencia y tecnología", url: "https://www.xataka.com/feed", category_id: 13000000 },
  { medio: "Xataka", rss: "Cultura", url: "https://www.xatakasensacine.com/feed", category_id: 1000000 },
  { medio: "Xataka", rss: "Telecomunicaciones", url: "https://www.xatakamovil.com/feed", category_id: 13000000 },
  { medio: "Xataka", rss: "Arte", url: "https://www.xatakafoto.com/feed", category_id: 1000000 },
  { medio: "Xataka", rss: "Ciencia y tecnología 2", url: "https://www.xatakahome.com/feed", category_id: 13000000 },
  { medio: "Cinco Días", rss: "Economía", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/portada", category_id: 4000000 },
  { medio: "Cinco Días", rss: "Mercados bursátiles", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/section/mercados", category_id: 4000000 },
  { medio: "Cinco Días", rss: "Empresas", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/section/companias", category_id: 4000000 },
  { medio: "Cinco Días", rss: "Economía 2", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/section/emprendedores", category_id: 4000000 },
  { medio: "Cinco Días", rss: "Economía 3", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/section/fortuna", category_id: 4000000 },
  { medio: "Marca", rss: "Deporte", url: "https://e00-marca.uecdn.es/rss/portada.xml", category_id: 15000000 },
  { medio: "Marca", rss: "Fútbol", url: "https://e00-marca.uecdn.es/rss/futbol/primera-division.xml", category_id: 15000000 },
  { medio: "Marca", rss: "Baloncesto", url: "https://e00-marca.uecdn.es/rss/baloncesto.xml", category_id: 15000000 },
  { medio: "Marca", rss: "Automovilismo", url: "https://e00-marca.uecdn.es/rss/motor/formula1.xml", category_id: 15000000 },
  { medio: "Marca", rss: "Tenis", url: "https://e00-marca.uecdn.es/rss/tenis.xml", category_id: 15000000 },
  { medio: "BBC News", rss: "Diplomacia", url: "https://feeds.bbci.co.uk/mundo/rss.xml", category_id: 11000000 },
  { medio: "BBC News", rss: "Política", url: "https://feeds.bbci.co.uk/mundo/temas/america_latina/rss.xml", category_id: 11000000 },
  { medio: "BBC News", rss: "Diplomacia 2", url: "https://feeds.bbci.co.uk/mundo/temas/internacional/rss.xml", category_id: 11000000 },
  { medio: "BBC News", rss: "Ciencia y tecnología", url: "https://feeds.bbci.co.uk/mundo/temas/ciencia/rss.xml", category_id: 13000000 },
  { medio: "BBC News", rss: "Cultura", url: "https://feeds.bbci.co.uk/mundo/temas/cultura/rss.xml", category_id: 1000000 },
  { medio: "La Vanguardia", rss: "Política", url: "https://www.lavanguardia.com/rss/home.xml", category_id: 11000000 },
  { medio: "La Vanguardia", rss: "Política 2", url: "https://www.lavanguardia.com/rss/politica.xml", category_id: 11000000 },
  { medio: "La Vanguardia", rss: "Economía", url: "https://www.lavanguardia.com/rss/economia.xml", category_id: 4000000 },
  { medio: "La Vanguardia", rss: "Cultura", url: "https://www.lavanguardia.com/rss/cultura.xml", category_id: 1000000 },
  { medio: "La Vanguardia", rss: "Deporte", url: "https://www.lavanguardia.com/rss/deportes.xml", category_id: 15000000 },
  { medio: "National Geographic", rss: "Ciencia y tecnología", url: "https://www.nationalgeographic.com.es/rss/ciencia.xml", category_id: 13000000 },
  { medio: "National Geographic", rss: "Historia", url: "https://www.nationalgeographic.com.es/rss/historia.xml", category_id: 1000000 },
  { medio: "National Geographic", rss: "Medio ambiente", url: "https://www.nationalgeographic.com.es/rss/naturaleza.xml", category_id: 6000000 },
  { medio: "National Geographic", rss: "Estilo de vida", url: "https://www.nationalgeographic.com.es/rss/viajes.xml", category_id: 10000000 },
  { medio: "National Geographic", rss: "Arte", url: "https://www.nationalgeographic.com.es/rss/fotografia.xml", category_id: 1000000 },
  { medio: "El País", rss: "Ciencia y tecnología 2", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/ciencia", category_id: 13000000 },
  { medio: "El País", rss: "Educación", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/educacion", category_id: 5000000 },
  { medio: "El País", rss: "Opinión", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/opinion", category_id: 11000000 },
  { medio: "El País", rss: "Asuntos sociales", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/sociedad", category_id: 14000000 },
  { medio: "El País", rss: "Estilo de vida", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/estilo", category_id: 10000000 },
  { medio: "El Mundo", rss: "Diplomacia", url: "https://www.elmundo.es/rss/internacional.xml", category_id: 11000000 },
  { medio: "El Mundo", rss: "Política 3", url: "https://www.elmundo.es/rss/madrid.xml", category_id: 11000000 },
  { medio: "El Mundo", rss: "Cultura", url: "https://www.elmundo.es/rss/cultura.xml", category_id: 1000000 },
  { medio: "El Mundo", rss: "Opinión", url: "https://www.elmundo.es/rss/opinion.xml", category_id: 11000000 },
  { medio: "El Mundo", rss: "Entretenimiento", url: "https://www.elmundo.es/rss/television.xml", category_id: 1000000 },
  { medio: "ABC", rss: "Economía", url: "https://www.abc.es/rss/2.0/economia/", category_id: 4000000 },
  { medio: "ABC", rss: "Deporte", url: "https://www.abc.es/rss/2.0/deportes/", category_id: 15000000 },
  { medio: "ABC", rss: "Estilo de vida", url: "https://www.abc.es/rss/2.0/estilo/", category_id: 10000000 },
  { medio: "ABC", rss: "Ciencia y tecnología 2", url: "https://www.abc.es/rss/2.0/tecnologia/", category_id: 13000000 },
  { medio: "ABC", rss: "Opinión", url: "https://www.abc.es/rss/2.0/opinion/", category_id: 11000000 },
  { medio: "El Confidencial", rss: "Política", url: "https://rss.elconfidencial.com/espana/", category_id: 11000000 },
  { medio: "El Confidencial", rss: "Diplomacia", url: "https://rss.elconfidencial.com/mundo/", category_id: 11000000 },
  { medio: "El Confidencial", rss: "Economía", url: "https://rss.elconfidencial.com/economia/", category_id: 4000000 },
  { medio: "El Confidencial", rss: "Ciencia y tecnología", url: "https://rss.elconfidencial.com/tecnologia/", category_id: 13000000 },
  { medio: "El Confidencial", rss: "Deporte", url: "https://rss.elconfidencial.com/deportes/", category_id: 15000000 },
  { medio: "Infobae", rss: "Política", url: "https://www.infobae.com/feeds/rss/", category_id: 11000000 },
  { medio: "Infobae", rss: "Diplomacia", url: "https://www.infobae.com/america/rss/", category_id: 11000000 },
  { medio: "Infobae", rss: "Economía", url: "https://www.infobae.com/economia/rss/", category_id: 4000000 },
  { medio: "Infobae", rss: "Deporte", url: "https://www.infobae.com/deportes/rss/", category_id: 15000000 },
  { medio: "Infobae", rss: "Cultura", url: "https://www.infobae.com/teleshow/rss/", category_id: 1000000 },
  { medio: "El Español", rss: "Política", url: "https://www.elespanol.com/rss/", category_id: 11000000 },
  { medio: "El Español", rss: "Política 2", url: "https://www.elespanol.com/rss/espana/", category_id: 11000000 },
  { medio: "El Español", rss: "Economía", url: "https://www.elespanol.com/rss/economia/", category_id: 4000000 },
  { medio: "El Español", rss: "Ciencia y tecnología", url: "https://www.elespanol.com/rss/ciencia/", category_id: 13000000 },
  { medio: "El Español", rss: "Deporte", url: "https://www.elespanol.com/rss/deportes/", category_id: 15000000 },
  { medio: "El Diario.es", rss: "Política", url: "https://www.eldiario.es/rss/", category_id: 11000000 },
  { medio: "El Diario.es", rss: "Diplomacia", url: "https://www.eldiario.es/rss/internacional/", category_id: 11000000 },
  { medio: "El Diario.es", rss: "Economía", url: "https://www.eldiario.es/rss/economia/", category_id: 4000000 },
  { medio: "El Diario.es", rss: "Cultura", url: "https://www.eldiario.es/rss/cultura/", category_id: 1000000 },
  { medio: "El Diario.es", rss: "Ciencia y tecnología", url: "https://www.eldiario.es/rss/tecnologia/", category_id: 13000000 },
  { medio: "20 Minutos", rss: "Política", url: "https://www.20minutos.es/rss/", category_id: 11000000 },
  { medio: "20 Minutos", rss: "Política 2", url: "https://www.20minutos.es/rss/nacional/", category_id: 11000000 },
  { medio: "20 Minutos", rss: "Economía", url: "https://www.20minutos.es/rss/economia/", category_id: 4000000 },
  { medio: "20 Minutos", rss: "Deporte", url: "https://www.20minutos.es/rss/deportes/", category_id: 15000000 },
  { medio: "20 Minutos", rss: "Ciencia y tecnología", url: "https://www.20minutos.es/rss/tecnologia/", category_id: 13000000 },
  { medio: "La Razón", rss: "Política", url: "https://www.larazon.es/rss/espana.xml", category_id: 11000000 },
  { medio: "La Razón", rss: "Diplomacia", url: "https://www.larazon.es/rss/internacional.xml", category_id: 11000000 },
  { medio: "La Razón", rss: "Economía", url: "https://www.larazon.es/rss/economia.xml", category_id: 4000000 },
  { medio: "La Razón", rss: "Asuntos sociales", url: "https://www.larazon.es/rss/sociedad.xml", category_id: 14000000 },
  { medio: "La Razón", rss: "Cultura", url: "https://www.larazon.es/rss/cultura.xml", category_id: 1000000 },
  { medio: "Reuters", rss: "Diplomacia", url: "https://news.google.com/rss/search?q=reuters+español&hl=es-419&gl=US&ceid=US:es-419", category_id: 11000000 },
  { medio: "Reuters", rss: "Economía", url: "https://news.google.com/rss/search?q=reuters+economia&hl=es-419&gl=US&ceid=US:es-419", category_id: 4000000 },
  { medio: "Europa Press", rss: "Política", url: "https://www.europapress.es/rss/rss.aspx?ch=00066", category_id: 11000000 },
  { medio: "Europa Press", rss: "Diplomacia", url: "https://www.europapress.es/rss/rss.aspx?ch=00069", category_id: 11000000 },
  { medio: "Europa Press", rss: "Economía", url: "https://www.europapress.es/rss/rss.aspx?ch=00176", category_id: 4000000 },
  { medio: "AS", rss: "Deporte", url: "https://as.com/rss/tags/ultimas_noticias.xml", category_id: 15000000 },
  { medio: "AS", rss: "Fútbol", url: "https://as.com/rss/tags/futbol.xml", category_id: 15000000 },
  { medio: "AS", rss: "Baloncesto", url: "https://as.com/rss/tags/nba.xml", category_id: 15000000 },
  { medio: "AS", rss: "Automovilismo", url: "https://as.com/rss/tags/formula_1.xml", category_id: 15000000 },
  { medio: "AS", rss: "Tenis", url: "https://as.com/rss/tags/tenis.xml", category_id: 15000000 },
  { medio: "Público", rss: "Política", url: "https://www.publico.es/rss", category_id: 11000000 },
  { medio: "Público", rss: "Política 2", url: "https://www.publico.es/rss/politica", category_id: 11000000 },
  { medio: "Público", rss: "Economía", url: "https://www.publico.es/rss/economia", category_id: 4000000 },
  { medio: "Público", rss: "Asuntos sociales", url: "https://www.publico.es/rss/sociedad", category_id: 14000000 },
  { medio: "Público", rss: "Cultura", url: "https://www.publico.es/rss/cultura", category_id: 1000000 },
  { medio: "Expansión", rss: "Economía", url: "https://e00-expansion.uecdn.es/rss/portada.xml", category_id: 4000000 },
  { medio: "Expansión", rss: "Mercados bursátiles", url: "https://e00-expansion.uecdn.es/rss/mercados.xml", category_id: 4000000 },
  { medio: "Expansión", rss: "Empresas", url: "https://e00-expansion.uecdn.es/rss/empresas.xml", category_id: 4000000 },
  { medio: "Expansión", rss: "Economía 2", url: "https://e00-expansion.uecdn.es/rss/economia.xml", category_id: 4000000 },
  { medio: "Expansión", rss: "Ciencia y tecnología", url: "https://e00-expansion.uecdn.es/rss/tecnologia.xml", category_id: 13000000 },
  { medio: "El Periódico", rss: "Política", url: "https://www.elperiodico.com/es/rss/rss_portada.xml", category_id: 11000000 },
  { medio: "El Periódico", rss: "Política 2", url: "https://www.elperiodico.com/es/rss/rss_politica.xml", category_id: 11000000 },
  { medio: "El Periódico", rss: "Economía", url: "https://www.elperiodico.com/es/rss/rss_economia.xml", category_id: 4000000 },
  { medio: "El Periódico", rss: "Deporte", url: "https://www.elperiodico.com/es/rss/rss_deportes.xml", category_id: 15000000 },
  { medio: "El Periódico", rss: "Asuntos sociales", url: "https://www.elperiodico.com/es/rss/rss_sociedad.xml", category_id: 14000000 },
  { medio: "EFE", rss: "Política", url: "https://www.efe.com/efe/espana/portada/1?format=rss", category_id: 11000000 },
  { medio: "EFE", rss: "Diplomacia", url: "https://www.efe.com/efe/espana/mundo/1?format=rss", category_id: 11000000 },
  { medio: "EFE", rss: "Economía", url: "https://www.efe.com/efe/espana/economia/1?format=rss", category_id: 4000000 },
  { medio: "EFE", rss: "Cultura", url: "https://www.efe.com/efe/espana/cultura/1?format=rss", category_id: 1000000 },
  { medio: "EFE", rss: "Deporte", url: "https://www.efe.com/efe/espana/deportes/1?format=rss", category_id: 15000000 },
  { medio: "EFE", rss: "Ciencia y tecnología", url: "https://www.efe.com/efe/espana/tecnologia/1?format=rss", category_id: 13000000 },
  { medio: "DW Español", rss: "Política", url: "https://rss.dw.com/rdf/rss-es-noticias", category_id: 11000000 },
  { medio: "DW Español", rss: "Diplomacia", url: "https://rss.dw.com/rdf/rss-es-america-latina", category_id: 11000000 },
  { medio: "DW Español", rss: "Economía", url: "https://rss.dw.com/rdf/rss-es-economia", category_id: 4000000 },
  { medio: "DW Español", rss: "Ciencia y tecnología", url: "https://rss.dw.com/rdf/rss-es-ciencia", category_id: 13000000 },
  { medio: "DW Español", rss: "Cultura", url: "https://rss.dw.com/rdf/rss-es-cultura", category_id: 1000000 },
  { medio: "France 24", rss: "Política", url: "https://www.france24.com/es/rss", category_id: 11000000 },
  { medio: "France 24", rss: "Política 2", url: "https://www.france24.com/es/europa/rss", category_id: 11000000 },
  { medio: "France 24", rss: "Diplomacia", url: "https://www.france24.com/es/americas/rss", category_id: 11000000 },
  { medio: "France 24", rss: "Economía", url: "https://www.france24.com/es/economia/rss", category_id: 4000000 },
  { medio: "France 24", rss: "Cultura", url: "https://www.france24.com/es/cultura/rss", category_id: 1000000 },
  { medio: "The Guardian", rss: "Diplomacia", url: "https://www.theguardian.com/world/rss", category_id: 11000000 },
  { medio: "The Guardian", rss: "Política", url: "https://www.theguardian.com/politics/rss", category_id: 11000000 },
  { medio: "The Guardian", rss: "Economía", url: "https://www.theguardian.com/business/rss", category_id: 4000000 },
  { medio: "The Guardian", rss: "Ciencia y tecnología", url: "https://www.theguardian.com/science/rss", category_id: 13000000 },
  { medio: "The Guardian", rss: "Cultura", url: "https://www.theguardian.com/culture/rss", category_id: 1000000 },
  { medio: "elEconomista", rss: "Economía", url: "https://www.eleconomista.es/rss/rss-economia.php", category_id: 4000000 },
  { medio: "elEconomista", rss: "Mercados bursátiles", url: "https://www.eleconomista.es/rss/rss-mercados.php", category_id: 4000000 },
  { medio: "elEconomista", rss: "Empresas", url: "https://www.eleconomista.es/rss/rss-empresas.php", category_id: 4000000 },
  { medio: "elEconomista", rss: "Ciencia y tecnología", url: "https://www.eleconomista.es/rss/rss-tecnologia.php", category_id: 13000000 },
  { medio: "elEconomista", rss: "Política", url: "https://www.eleconomista.es/rss/rss-espana.php", category_id: 11000000 },
  { medio: "Vozpópuli", rss: "Política", url: "https://vozpopuli.com/politica/feed/", category_id: 11000000 },
  { medio: "Vozpópuli", rss: "Economía", url: "https://vozpopuli.com/economia/feed/", category_id: 4000000 },
  { medio: "Vozpópuli", rss: "Asuntos sociales", url: "https://vozpopuli.com/sociedad/feed/", category_id: 14000000 },
  { medio: "Vozpópuli", rss: "Cultura", url: "https://vozpopuli.com/cultura/feed/", category_id: 1000000 },
  { medio: "Vozpópuli", rss: "Deporte", url: "https://vozpopuli.com/deporte/feed/", category_id: 15000000 },
  { medio: "OKDiario", rss: "Política", url: "https://okdiario.com/espana/feed/", category_id: 11000000 },
  { medio: "OKDiario", rss: "Economía", url: "https://okdiario.com/economia/feed/", category_id: 4000000 },
  { medio: "OKDiario", rss: "Deporte", url: "https://okdiario.com/deporte/feed/", category_id: 15000000 },
  { medio: "OKDiario", rss: "Asuntos sociales", url: "https://okdiario.com/sociedad/feed/", category_id: 14000000 },
  { medio: "OKDiario", rss: "Cultura", url: "https://okdiario.com/cultura/feed/", category_id: 1000000 },
  { medio: "Heraldo de Aragón", rss: "Política", url: "https://www.heraldo.es/noticias/rss.xml", category_id: 11000000 },
  { medio: "Heraldo de Aragón", rss: "Política 2", url: "https://www.heraldo.es/noticias/aragon/rss.xml", category_id: 11000000 },
  { medio: "Heraldo de Aragón", rss: "Política 3", url: "https://www.heraldo.es/noticias/zaragoza/rss.xml", category_id: 11000000 },
  { medio: "Heraldo de Aragón", rss: "Economía", url: "https://www.heraldo.es/noticias/economia/rss.xml", category_id: 4000000 },
  { medio: "Heraldo de Aragón", rss: "Deporte", url: "https://www.heraldo.es/noticias/deportes/rss.xml", category_id: 15000000 },
  { medio: "Sport", rss: "Deporte", url: "https://www.sport.es/es/rss/rss.xml", category_id: 15000000 },
  { medio: "Sport", rss: "Fútbol", url: "https://www.sport.es/es/noticias/fc-barcelona/rss.xml", category_id: 15000000 },
  { medio: "Sport", rss: "Baloncesto", url: "https://www.sport.es/es/noticias/nba/rss.xml", category_id: 15000000 },
  { medio: "Sport", rss: "Tenis", url: "https://www.sport.es/es/noticias/tenis/rss.xml", category_id: 15000000 },
  { medio: "Sport", rss: "Automovilismo", url: "https://www.sport.es/es/noticias/motor/rss.xml", category_id: 15000000 },
  { medio: "El Mundo", rss: "Policía y justicia", url: "https://www.elmundo.es/rss/cronica-negra.xml", category_id: 2000000 },
  { medio: "ABC", rss: "Policía y justicia", url: "https://www.abc.es/rss/2.0/sucesos/", category_id: 2000000 },
  { medio: "El País", rss: "Catástrofes y accidentes", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/clima-y-medio-ambiente", category_id: 3000000 },
  { medio: "RTVE", rss: "Catástrofes y accidentes", url: "https://www.rtve.es/noticias/rss/emergencias.xml", category_id: 3000000 },
  { medio: "20 Minutos", rss: "Interés humano", url: "https://www.20minutos.es/rss/gente/", category_id: 8000000 },
  { medio: "El Mundo", rss: "Interés humano", url: "https://www.elmundo.es/rss/gente.xml", category_id: 8000000 },
  { medio: "Expansión", rss: "Mano de obra", url: "https://e00-expansion.uecdn.es/rss/empleo.xml", category_id: 9000000 },
  { medio: "El País", rss: "Mano de obra", url: "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/empleo", category_id: 9000000 },
  { medio: "Vatican News", rss: "Religión y culto", url: "https://www.vaticannews.va/es/rss.xml", category_id: 12000000 },
  { medio: "ABC", rss: "Religión y culto", url: "https://www.abc.es/rss/2.0/religion/", category_id: 12000000 },
  { medio: "BBC News", rss: "Conflicto, guerra y paz", url: "https://feeds.bbci.co.uk/mundo/temas/guerra/rss.xml", category_id: 16000000 },
  { medio: "DW Español", rss: "Conflicto, guerra y paz", url: "https://rss.dw.com/rdf/rss-es-seguridad", category_id: 16000000 },
  { medio: "El Tiempo", rss: "Meteorología", url: "https://www.eltiempo.es/rss/rss.xml", category_id: 17000000 },
  { medio: "RTVE", rss: "Meteorología", url: "https://www.rtve.es/noticias/rss/tiempo.xml", category_id: 17000000 },
];

function nextCounter(name) {
  const result = db.getCollection("counters").findOneAndUpdate(
    { _id: name },
    {
      $inc: { seq: NumberInt(1) },
      $set: { updated_at: new Date() },
    },
    {
      upsert: true,
      returnDocument: "after",
    }
  );
  return NumberInt(result.seq);
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

function sourceNameFromMedium(medio) {
  return medio
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function sourceUrlFromFeedUrl(feedUrl) {
  const parsed = new URL(feedUrl);
  return `${parsed.protocol}//${parsed.host}`;
}

function seedStandardRssSources() {
  const sourcesCollection = db.getCollection("information_sources");
  const channelsCollection = db.getCollection("rss_channels");
  const now = new Date();
  const sourceIdsByMedium = {};

  STANDARD_RSS_SOURCES.forEach((source) => {
    if (sourceIdsByMedium[source.medio]) {
      return;
    }

    const sourceUrl = sourceUrlFromFeedUrl(source.url);
    let existingSource = sourcesCollection.findOne(
      { url: sourceUrl, deleted_at: { $exists: false } },
      { id: 1 }
    );
    if (!existingSource) {
      const sourceId = nextCounter("information_sources");
      sourcesCollection.insertOne({
        id: sourceId,
        name: sourceNameFromMedium(source.medio),
        url: sourceUrl,
        active: true,
        created_at: now,
        updated_at: now,
      });
      existingSource = { id: sourceId };
    } else {
      sourcesCollection.updateOne(
        { id: existingSource.id },
        {
          $set: {
            name: sourceNameFromMedium(source.medio),
            active: true,
            updated_at: now,
          },
        }
      );
    }
    sourceIdsByMedium[source.medio] = NumberInt(existingSource.id);
  });

  STANDARD_RSS_SOURCES.forEach((source) => {
    const existingChannel = channelsCollection.findOne(
      { url: source.url, deleted_at: { $exists: false } },
      { id: 1 }
    );
    const channelId = existingChannel ? existingChannel.id : nextCounter("rss_channels");
    channelsCollection.updateOne(
      { id: channelId },
      {
        $set: {
          id: channelId,
          information_source_id: sourceIdsByMedium[source.medio],
          url: source.url,
          active: true,
          category_id: NumberInt(source.category_id),
          updated_at: now,
        },
        $setOnInsert: {
          created_at: now,
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


