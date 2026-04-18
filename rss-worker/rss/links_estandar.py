from .parsers import *

from .RSSFuente import RSSFuente

def generar_lista_estandar_feeds() -> list[RSSFuente]:
    feeds = [
        RSSFuente(
            "el_pais",
            "",
            "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
        ),
        RSSFuente("abc", "", "https://www.abc.es/rss/feeds/abcPortada.xml"),
        RSSFuente("bbc", "mundo", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        RSSFuente(
            "rtve", "noticias", "https://api2.rtve.es/rss/temas_noticias.xml"
        ),
        RSSFuente(
            "elconfidencial", "mundo", "https://rss.elconfidencial.com/mundo/"
        ),
        RSSFuente(
            "marca",
            "primera_division",
            "https://objetos.estaticos-marca.com/rss/futbol/primera-division.xml",
        ),
        RSSFuente("esdiario", "", "https://www.esdiario.com/rss/home.xml"),
        RSSFuente(
            "antena3", "", "https://www.antena3.com/noticias/rss/4013050.xml"
        ),
        RSSFuente(
            "ministerio_dsa",
            "",
            "https://www.dsca.gob.es/es/rss-noticias.xml",
        ),
        RSSFuente("moncloa", "", "https://www.lamoncloa.gob.es/paginas/rss.aspx")
    ]

    return feeds

__all__ = ["generar_lista_estandar_feeds"]
