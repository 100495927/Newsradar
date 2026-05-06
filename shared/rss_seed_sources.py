from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class RSSSeedSource:
    medio: str
    rss: str
    url: str
    activo: bool = True
    category_id: int | None = None

    @property
    def hash_fuente(self) -> str:
        raw = f"{self.medio}{self.rss}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def to_mongo(self, now: datetime | None = None) -> dict:
        timestamp = now or datetime.now(timezone.utc)
        return {
            "hash_fuente": self.hash_fuente,
            "medio": self.medio,
            "rss": self.rss,
            "url": self.url,
            "tipo": "channel",
            "activo": self.activo,
            "category_id": self.category_id,
            "creado": timestamp,
            "actualizado": timestamp,
        }


STANDARD_RSS_SOURCES: tuple[RSSSeedSource, ...] = (
    RSSSeedSource("El País", "Economía", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", category_id=4000000),
    RSSSeedSource("El País", "Política", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional", category_id=11000000),
    RSSSeedSource("El País", "Deporte", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/deportes", category_id=15000000),
    RSSSeedSource("El País", "Cultura", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/cultura", category_id=1000000),
    RSSSeedSource("El País", "Ciencia y tecnología", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia", category_id=13000000),
    RSSSeedSource("El Mundo", "Política", "https://www.elmundo.es/rss/portada.xml", category_id=11000000),
    RSSSeedSource("El Mundo", "Política 2", "https://www.elmundo.es/rss/espana.xml", category_id=11000000),
    RSSSeedSource("El Mundo", "Economía", "https://www.elmundo.es/rss/economia.xml", category_id=4000000),
    RSSSeedSource("El Mundo", "Salud", "https://www.elmundo.es/rss/ciencia-y-salud.xml", category_id=7000000),
    RSSSeedSource("El Mundo", "Deporte", "https://www.elmundo.es/rss/deportes.xml", category_id=15000000),
    RSSSeedSource("ABC", "Política", "https://www.abc.es/rss/2.0/portada/", category_id=11000000),
    RSSSeedSource("ABC", "Diplomacia", "https://www.abc.es/rss/2.0/internacional/", category_id=11000000),
    RSSSeedSource("ABC", "Asuntos sociales", "https://www.abc.es/rss/2.0/sociedad/", category_id=14000000),
    RSSSeedSource("ABC", "Cultura", "https://www.abc.es/rss/2.0/cultura/", category_id=1000000),
    RSSSeedSource("ABC", "Ciencia y tecnología", "https://www.abc.es/rss/2.0/ciencia/", category_id=13000000),
    RSSSeedSource("RTVE", "Política", "https://www.rtve.es/noticias/rss/noticias.xml", category_id=11000000),
    RSSSeedSource("RTVE", "Diplomacia", "https://www.rtve.es/noticias/rss/mundo.xml", category_id=11000000),
    RSSSeedSource("RTVE", "Ciencia y tecnología", "https://www.rtve.es/noticias/rss/tecnologia.xml", category_id=13000000),
    RSSSeedSource("RTVE", "Cultura", "https://www.rtve.es/noticias/rss/cultura.xml", category_id=1000000),
    RSSSeedSource("RTVE", "Deporte", "https://www.rtve.es/noticias/rss/deportes.xml", category_id=15000000),
    RSSSeedSource("Xataka", "Ciencia y tecnología", "https://www.xataka.com/feed", category_id=13000000),
    RSSSeedSource("Xataka", "Cultura", "https://www.xatakasensacine.com/feed", category_id=1000000),
    RSSSeedSource("Xataka", "Telecomunicaciones", "https://www.xatakamovil.com/feed", category_id=13000000),
    RSSSeedSource("Xataka", "Arte", "https://www.xatakafoto.com/feed", category_id=1000000),
    RSSSeedSource("Xataka", "Ciencia y tecnología 2", "https://www.xatakahome.com/feed", category_id=13000000),
    RSSSeedSource("Cinco Días", "Economía", "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/portada", category_id=4000000),
    RSSSeedSource("Cinco Días", "Mercados bursátiles", "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/section/mercados", category_id=4000000),
    RSSSeedSource("Cinco Días", "Empresas", "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/section/companias", category_id=4000000),
    RSSSeedSource("Cinco Días", "Economía 2", "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/section/emprendedores", category_id=4000000),
    RSSSeedSource("Cinco Días", "Economía 3", "https://feeds.elpais.com/mrss-s/pages/ep/site/cincodias.com/section/fortuna", category_id=4000000),
    RSSSeedSource("Marca", "Deporte", "https://e00-marca.uecdn.es/rss/portada.xml", category_id=15000000),
    RSSSeedSource("Marca", "Fútbol", "https://e00-marca.uecdn.es/rss/futbol/primera-division.xml", category_id=15000000),
    RSSSeedSource("Marca", "Baloncesto", "https://e00-marca.uecdn.es/rss/baloncesto.xml", category_id=15000000),
    RSSSeedSource("Marca", "Automovilismo", "https://e00-marca.uecdn.es/rss/motor/formula1.xml", category_id=15000000),
    RSSSeedSource("Marca", "Tenis", "https://e00-marca.uecdn.es/rss/tenis.xml", category_id=15000000),
    RSSSeedSource("BBC News", "Diplomacia", "https://feeds.bbci.co.uk/mundo/rss.xml", category_id=11000000),
    RSSSeedSource("BBC News", "Política", "https://feeds.bbci.co.uk/mundo/temas/america_latina/rss.xml", category_id=11000000),
    RSSSeedSource("BBC News", "Diplomacia 2", "https://feeds.bbci.co.uk/mundo/temas/internacional/rss.xml", category_id=11000000),
    RSSSeedSource("BBC News", "Ciencia y tecnología", "https://feeds.bbci.co.uk/mundo/temas/ciencia/rss.xml", category_id=13000000),
    RSSSeedSource("BBC News", "Cultura", "https://feeds.bbci.co.uk/mundo/temas/cultura/rss.xml", category_id=1000000),
    RSSSeedSource("La Vanguardia", "Política", "https://www.lavanguardia.com/rss/home.xml", category_id=11000000),
    RSSSeedSource("La Vanguardia", "Política 2", "https://www.lavanguardia.com/rss/politica.xml", category_id=11000000),
    RSSSeedSource("La Vanguardia", "Economía", "https://www.lavanguardia.com/rss/economia.xml", category_id=4000000),
    RSSSeedSource("La Vanguardia", "Cultura", "https://www.lavanguardia.com/rss/cultura.xml", category_id=1000000),
    RSSSeedSource("La Vanguardia", "Deporte", "https://www.lavanguardia.com/rss/deportes.xml", category_id=15000000),
    RSSSeedSource("National Geographic", "Ciencia y tecnología", "https://www.nationalgeographic.com.es/rss/ciencia.xml", category_id=13000000),
    RSSSeedSource("National Geographic", "Historia", "https://www.nationalgeographic.com.es/rss/historia.xml", category_id=1000000),
    RSSSeedSource("National Geographic", "Medio ambiente", "https://www.nationalgeographic.com.es/rss/naturaleza.xml", category_id=6000000),
    RSSSeedSource("National Geographic", "Estilo de vida", "https://www.nationalgeographic.com.es/rss/viajes.xml", category_id=10000000),
    RSSSeedSource("National Geographic", "Arte", "https://www.nationalgeographic.com.es/rss/fotografia.xml", category_id=1000000),
    RSSSeedSource("El País", "Ciencia y tecnología 2", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/ciencia", category_id=13000000),
    RSSSeedSource("El País", "Educación", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/educacion", category_id=5000000),
    RSSSeedSource("El País", "Opinión", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/opinion", category_id=11000000),
    RSSSeedSource("El País", "Asuntos sociales", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/sociedad", category_id=14000000),
    RSSSeedSource("El País", "Estilo de vida", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/estilo", category_id=10000000),
    RSSSeedSource("El Mundo", "Diplomacia", "https://www.elmundo.es/rss/internacional.xml", category_id=11000000),
    RSSSeedSource("El Mundo", "Política 3", "https://www.elmundo.es/rss/madrid.xml", category_id=11000000),
    RSSSeedSource("El Mundo", "Cultura", "https://www.elmundo.es/rss/cultura.xml", category_id=1000000),
    RSSSeedSource("El Mundo", "Opinión", "https://www.elmundo.es/rss/opinion.xml", category_id=11000000),
    RSSSeedSource("El Mundo", "Entretenimiento", "https://www.elmundo.es/rss/television.xml", category_id=1000000),
    RSSSeedSource("ABC", "Economía", "https://www.abc.es/rss/2.0/economia/", category_id=4000000),
    RSSSeedSource("ABC", "Deporte", "https://www.abc.es/rss/2.0/deportes/", category_id=15000000),
    RSSSeedSource("ABC", "Estilo de vida", "https://www.abc.es/rss/2.0/estilo/", category_id=10000000),
    RSSSeedSource("ABC", "Ciencia y tecnología 2", "https://www.abc.es/rss/2.0/tecnologia/", category_id=13000000),
    RSSSeedSource("ABC", "Opinión", "https://www.abc.es/rss/2.0/opinion/", category_id=11000000),
    RSSSeedSource("El Confidencial", "Política", "https://rss.elconfidencial.com/espana/", category_id=11000000),
    RSSSeedSource("El Confidencial", "Diplomacia", "https://rss.elconfidencial.com/mundo/", category_id=11000000),
    RSSSeedSource("El Confidencial", "Economía", "https://rss.elconfidencial.com/economia/", category_id=4000000),
    RSSSeedSource("El Confidencial", "Ciencia y tecnología", "https://rss.elconfidencial.com/tecnologia/", category_id=13000000),
    RSSSeedSource("El Confidencial", "Deporte", "https://rss.elconfidencial.com/deportes/", category_id=15000000),
    RSSSeedSource("Infobae", "Política", "https://www.infobae.com/feeds/rss/", category_id=11000000),
    RSSSeedSource("Infobae", "Diplomacia", "https://www.infobae.com/america/rss/", category_id=11000000),
    RSSSeedSource("Infobae", "Economía", "https://www.infobae.com/economia/rss/", category_id=4000000),
    RSSSeedSource("Infobae", "Deporte", "https://www.infobae.com/deportes/rss/", category_id=15000000),
    RSSSeedSource("Infobae", "Cultura", "https://www.infobae.com/teleshow/rss/", category_id=1000000),
    RSSSeedSource("El Español", "Política", "https://www.elespanol.com/rss/", category_id=11000000),
    RSSSeedSource("El Español", "Política 2", "https://www.elespanol.com/rss/espana/", category_id=11000000),
    RSSSeedSource("El Español", "Economía", "https://www.elespanol.com/rss/economia/", category_id=4000000),
    RSSSeedSource("El Español", "Ciencia y tecnología", "https://www.elespanol.com/rss/ciencia/", category_id=13000000),
    RSSSeedSource("El Español", "Deporte", "https://www.elespanol.com/rss/deportes/", category_id=15000000),
    RSSSeedSource("El Diario.es", "Política", "https://www.eldiario.es/rss/", category_id=11000000),
    RSSSeedSource("El Diario.es", "Diplomacia", "https://www.eldiario.es/rss/internacional/", category_id=11000000),
    RSSSeedSource("El Diario.es", "Economía", "https://www.eldiario.es/rss/economia/", category_id=4000000),
    RSSSeedSource("El Diario.es", "Cultura", "https://www.eldiario.es/rss/cultura/", category_id=1000000),
    RSSSeedSource("El Diario.es", "Ciencia y tecnología", "https://www.eldiario.es/rss/tecnologia/", category_id=13000000),
    RSSSeedSource("20 Minutos", "Política", "https://www.20minutos.es/rss/", category_id=11000000),
    RSSSeedSource("20 Minutos", "Política 2", "https://www.20minutos.es/rss/nacional/", category_id=11000000),
    RSSSeedSource("20 Minutos", "Economía", "https://www.20minutos.es/rss/economia/", category_id=4000000),
    RSSSeedSource("20 Minutos", "Deporte", "https://www.20minutos.es/rss/deportes/", category_id=15000000),
    RSSSeedSource("20 Minutos", "Ciencia y tecnología", "https://www.20minutos.es/rss/tecnologia/", category_id=13000000),
    RSSSeedSource("La Razón", "Política", "https://www.larazon.es/rss/espana.xml", category_id=11000000),
    RSSSeedSource("La Razón", "Diplomacia", "https://www.larazon.es/rss/internacional.xml", category_id=11000000),
    RSSSeedSource("La Razón", "Economía", "https://www.larazon.es/rss/economia.xml", category_id=4000000),
    RSSSeedSource("La Razón", "Asuntos sociales", "https://www.larazon.es/rss/sociedad.xml", category_id=14000000),
    RSSSeedSource("La Razón", "Cultura", "https://www.larazon.es/rss/cultura.xml", category_id=1000000),
    RSSSeedSource("Reuters", "Diplomacia", "https://news.google.com/rss/search?q=reuters+español&hl=es-419&gl=US&ceid=US:es-419", category_id=11000000),
    RSSSeedSource("Reuters", "Economía", "https://news.google.com/rss/search?q=reuters+economia&hl=es-419&gl=US&ceid=US:es-419", category_id=4000000),
    RSSSeedSource("Europa Press", "Política", "https://www.europapress.es/rss/rss.aspx?ch=00066", category_id=11000000),
    RSSSeedSource("Europa Press", "Diplomacia", "https://www.europapress.es/rss/rss.aspx?ch=00069", category_id=11000000),
    RSSSeedSource("Europa Press", "Economía", "https://www.europapress.es/rss/rss.aspx?ch=00176", category_id=4000000),
)


def build_standard_rss_source_documents(now: datetime | None = None) -> list[dict]:
    return [source.to_mongo(now=now) for source in STANDARD_RSS_SOURCES]
