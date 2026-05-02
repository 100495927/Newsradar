from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

POLITICS = 11000000
SPORT = 15000000
SOCIETY = 14000000


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
    RSSSeedSource("el_pais", "portada", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", category_id=SOCIETY),
    RSSSeedSource("el_pais", "america", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/america/portada", category_id=POLITICS),
    RSSSeedSource("el_pais", "english", "https://feeds.elpais.com/mrss-s/pages/ep/site/english.elpais.com/portada", category_id=SOCIETY),
    RSSSeedSource("el_pais", "mexico", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/mexico/portada", category_id=POLITICS),
    RSSSeedSource("el_pais", "colombia", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/america-colombia/portada", category_id=POLITICS),
    RSSSeedSource("el_pais", "chile", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/chile/portada", category_id=POLITICS),
    RSSSeedSource("el_pais", "argentina", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/argentina/portada", category_id=POLITICS),
    RSSSeedSource("abcnews", "us", "https://abcnews.com/abcnews/usheadlines", category_id=SOCIETY),
    RSSSeedSource("abcnews", "international", "https://abcnews.com/abcnews/internationalheadlines", category_id=POLITICS),
    RSSSeedSource("abcnews", "politics", "https://abcnews.com/abcnews/politicsheadlines", category_id=POLITICS),
    RSSSeedSource("abc", "", "https://www.abc.es/rss/feeds/abcPortada.xml", category_id=SOCIETY),
    RSSSeedSource("bbc", "mundo", "https://feeds.bbci.co.uk/news/world/rss.xml", category_id=POLITICS),
    RSSSeedSource("rtve", "noticias", "https://api2.rtve.es/rss/temas_noticias.xml", category_id=SOCIETY),
    RSSSeedSource("elconfidencial", "mundo", "https://rss.elconfidencial.com/mundo/", category_id=POLITICS),
    RSSSeedSource("marca", "primera_division", "https://objetos.estaticos-marca.com/rss/futbol/primera-division.xml", category_id=SPORT),
    RSSSeedSource("marca", "segunda_division", "https://objetos.estaticos-marca.com/rss/futbol/segunda-division.xml", category_id=SPORT),
    RSSSeedSource("marca", "mas_futbol", "https://objetos.estaticos-marca.com/rss/futbol/mas-futbol.xml", category_id=SPORT),
    RSSSeedSource("marca", "copa_del_rey", "https://objetos.estaticos-marca.com/rss/futbol/copa-rey.xml", category_id=SPORT),
    RSSSeedSource("marca", "furbol_femenino", "https://objetos.estaticos-marca.com/rss/futbol/futbol-femenino.xml", category_id=SPORT),
    RSSSeedSource("marca", "seleccion_española", "https://objetos.estaticos-marca.com/rss/futbol/seleccion.xml", category_id=SPORT),
    RSSSeedSource("marca", "futbol_sala", "https://objetos.estaticos-marca.com/rss/futbol/futbol-sala.xml", category_id=SPORT),
    RSSSeedSource("marca", "futbol_internacional", "https://objetos.estaticos-marca.com/rss/futbol/futbol-internacional.xml", category_id=SPORT),
    RSSSeedSource("marca", "champions_league", "https://objetos.estaticos-marca.com/rss/futbol/champions-league.xml", category_id=SPORT),
    RSSSeedSource("marca", "europa_league", "https://objetos.estaticos-marca.com/rss/futbol/europa-league.xml", category_id=SPORT),
    RSSSeedSource("marca", "premier_league", "https://objetos.estaticos-marca.com/rss/futbol/premier-league.xml", category_id=SPORT),
    RSSSeedSource("marca", "bundersliga", "https://objetos.estaticos-marca.com/rss/futbol/bundesliga.xml", category_id=SPORT),
    RSSSeedSource("marca", "liga_italiana", "https://objetos.estaticos-marca.com/rss/futbol/liga-italiana.xml", category_id=SPORT),
    RSSSeedSource("marca", "liga_francesa", "https://objetos.estaticos-marca.com/rss/futbol/liga-francesa.xml", category_id=SPORT),
    RSSSeedSource("marca", "mundial_de_clubes", "https://objetos.estaticos-marca.com/rss/futbol/mundial-de-clubes.xml", category_id=SPORT),
    RSSSeedSource("marca", "america", "https://objetos.estaticos-marca.com/rss/futbol/america.xml", category_id=SPORT),
    RSSSeedSource("esdiario", "", "https://www.esdiario.com/rss/home.xml", category_id=SOCIETY),
    RSSSeedSource("antena3", "", "https://www.antena3.com/noticias/rss/4013050.xml", category_id=SOCIETY),
    RSSSeedSource("ministerio_dsa", "", "https://www.dsca.gob.es/es/rss-noticias.xml", category_id=POLITICS),
    RSSSeedSource("moncloa", "", "https://www.lamoncloa.gob.es/paginas/rss.aspx", category_id=POLITICS),
)


def build_standard_rss_source_documents(now: datetime | None = None) -> list[dict]:
    return [source.to_mongo(now=now) for source in STANDARD_RSS_SOURCES]
