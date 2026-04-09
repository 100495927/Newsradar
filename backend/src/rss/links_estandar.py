from rss.RSSFeedList import RSSFeedList
from .parsers import *


def generar_lista_estandar_feeds() -> RSSFeedList:
    feeds = [
        
    ]
    feeds.añadir(
        "el_pais",
        "",
        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
        RSSParser,
    )
    feeds.añadir("abc", "", "https://www.abc.es/rss/feeds/abcPortada.xml", RSSParser)
    feeds.añadir(
        "bbc", "mundo", "https://feeds.bbci.co.uk/news/world/rss.xml", RSSParser
    )
    feeds.añadir(
        "rtve", "noticias", "https://api2.rtve.es/rss/temas_noticias.xml", RSSParser
    )
    feeds.añadir(
        "elconfidencial", "mundo", "https://rss.elconfidencial.com/mundo/", RSSParser
    )
    feeds.añadir(
        "marca",
        "primera_division",
        "https://objetos.estaticos-marca.com/rss/futbol/primera-division.xml",
        RSSParser,
    )

    feeds.añadir(
        "esdiario", "", "https://www.esdiario.com/rss/home.xml", RSSParser
    )
    feeds.añadir(
        "antena3",
        "",
        "https://www.antena3.com/noticias/rss/4013050.xml",
        RSSParser,
    )
    feeds.añadir(
        "ministerio_dsa",
        "",
        "https://www.dsca.gob.es/es/rss-noticias.xml",
        MinisterioDSAParser,
    )
    feeds.añadir(
        "moncloa", "", "https://www.lamoncloa.gob.es/paginas/rss.aspx", RSSParser
    )

    return feeds


__all__ = ["generar_lista_estandar_feeds"]
