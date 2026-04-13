from .parsers import *

from .RSSFuente import RSSFuente

def generar_lista_estandar_feeds() -> list[RSSFuente]:
    feeds = [
        RSSFuente(
            "el_pais",
            "",
            "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
            RSSParser,
        ),
        RSSFuente("abc", "", "https://www.abc.es/rss/feeds/abcPortada.xml", RSSParser),
        RSSFuente("bbc", "mundo", "https://feeds.bbci.co.uk/news/world/rss.xml", RSSParser),
        RSSFuente(
            "rtve", "noticias", "https://api2.rtve.es/rss/temas_noticias.xml", RSSParser
        ),
        RSSFuente(
            "elconfidencial", "mundo", "https://rss.elconfidencial.com/mundo/", RSSParser
        ),
        RSSFuente(
            "marca",
            "primera_division",
            "https://objetos.estaticos-marca.com/rss/futbol/primera-division.xml",
            RSSParser,
        ),
        RSSFuente("esdiario", "", "https://www.esdiario.com/rss/home.xml", RSSParser),
        RSSFuente(
            "antena3", "", "https://www.antena3.com/noticias/rss/4013050.xml", RSSParser
        ),
        RSSFuente(
            "ministerio_dsa",
            "",
            "https://www.dsca.gob.es/es/rss-noticias.xml",
            MinisterioDSAParser,
        ),
        RSSFuente("moncloa", "", "https://www.lamoncloa.gob.es/paginas/rss.aspx", RSSParser)
    ]

    return feeds

__all__ = ["generar_lista_estandar_feeds"]
