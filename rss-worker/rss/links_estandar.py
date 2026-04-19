from .parsers import *

from .RSSFuente import RSSFuente

def generar_lista_estandar_feeds() -> list[RSSFuente]:
    feeds = [
        RSSFuente(
            "el_pais",
            "",
            "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
            categoria_iptc="Sociedad",
        ),
        RSSFuente(
            "abc",
            "",
            "https://www.abc.es/rss/feeds/abcPortada.xml",
            categoria_iptc="Sociedad",
        ),
        RSSFuente(
            "bbc",
            "mundo",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            categoria_iptc="Política",
        ),
        RSSFuente(
            "rtve",
            "noticias",
            "https://api2.rtve.es/rss/temas_noticias.xml",
            categoria_iptc="Sociedad",
        ),
        RSSFuente(
            "elconfidencial",
            "mundo",
            "https://rss.elconfidencial.com/mundo/",
            categoria_iptc="Política",
        ),
        RSSFuente(
            "marca",
            "primera_division",
            "https://objetos.estaticos-marca.com/rss/futbol/primera-division.xml",
            categoria_iptc="Deporte",
        ),
        RSSFuente(
            "esdiario",
            "",
            "https://www.esdiario.com/rss/home.xml",
            categoria_iptc="Sociedad",
        ),
        RSSFuente(
            "antena3",
            "",
            "https://www.antena3.com/noticias/rss/4013050.xml",
            categoria_iptc="Sociedad",
        ),
        RSSFuente(
            "ministerio_dsa",
            "",
            "https://www.dsca.gob.es/es/rss-noticias.xml",
            categoria_iptc="Política",
        ),
        RSSFuente(
            "moncloa",
            "",
            "https://www.lamoncloa.gob.es/paginas/rss.aspx",
            categoria_iptc="Política",
        ),
    ]

    return feeds

__all__ = ["generar_lista_estandar_feeds"]
