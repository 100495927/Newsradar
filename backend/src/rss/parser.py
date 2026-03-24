"""
Funciones para normalizar los rss de diferentes fuentes
"""

from feedparser import FeedParserDict
from dataclasses import dataclass
from datetime import datetime
from typing import Callable
import calendar


@dataclass
class RSSEntrada:
    titulo: str
    autores: list[str]
    link: str
    categorias: list[str]
    fecha_publicacion: int  # Unix timestamp
    resumen: str

    def __str__(self) -> str:
        return f"""
        {self.titulo}
        {self.autores}
        {self.link}
        {self.categorias}
        {datetime.fromtimestamp(self.fecha_publicacion).strftime('%H:%M %d/%m/%Y')}
        {self.resumen}
        """


def elpais_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = entrada.authors
    link = entrada.link
    categorias = [tag.term for tag in entrada.get("tags", [])]
    fecha_publicacion = calendar.timegm(entrada.published_parsed)
    for c in entrada.content:
        if c.type == "text/html":
            html = c.value
            break

    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [p.get_text(separator=" ", strip=True) for p in s.find_all("p")]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)


def abc_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = entrada.authors
    link = entrada.link
    categorias = [tag.term for tag in entrada.get("tags", [])]
    fecha_publicacion = calendar.timegm(entrada.published_parsed)
    html = entrada.description
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [p.get_text(separator=" ", strip=True) for p in s.find_all("p")]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)


def bbc_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = None
    link = entrada.link
    categorias = None
    fecha_publicacion = calendar.timegm(entrada.published_parsed)
    html = entrada.description
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [p.get_text(separator=" ", strip=True) for p in s.find_all("p")]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)


def rtve_noticias_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = None
    link = entrada.link
    categorias = None
    fecha_publicacion = calendar.timegm(entrada.published_parsed)
    html = entrada.description
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [li.get_text(separator=" ", strip=True) for li in s.find_all("li")]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)


def elconfidencial_mundo_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = entrada.authors
    link = entrada.link
    categorias = None
    fecha_publicacion = calendar.timegm(entrada.published_parsed)
    resumen = entrada.summary
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)


def marca_primera_division_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = entrada.authors
    link = entrada.link
    categorias = [tag.term for tag in entrada.get("tags", [])]
    fecha_publicacion = calendar.timegm(entrada.published_parsed)
    html = entrada.description
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = s.get_text(separator=" ", strip=False)
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)


def esdiario_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = entrada.authors
    link = entrada.link
    categorias = [tag.term for tag in entrada.get("tags", [])]
    fecha_publicacion = calendar.timegm(entrada.published_parsed)
    html = entrada.content[0].value
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [p.get_text(separator=" ", strip=True) for p in s.find_all("p")]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)


def antena3_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = entrada.authors
    link = entrada.link
    categorias = [tag.term for tag in entrada.get("tags", [])]
    fecha_publicacion = calendar.timegm(entrada.published_parsed)
    html = entrada.content[0].value
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [p.get_text(separator=" ", strip=True) for p in s.find_all("p")]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)


def ministerio_dsa_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = entrada.authors
    link = entrada.link
    categorias = None
    from dateparser import parse

    fecha_publicacion = int(parse(entrada.published).timestamp())
    html = entrada.description
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [
            p.get_text(separator=" ", strip=True)
            for p in s.find_all("p") + s.find_all("li")
        ]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)

def ministerio_eco_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = entrada.authors
    link = entrada.link
    categorias = None
    from dateparser import parse

    fecha_publicacion = int(parse(entrada.published).timestamp())
    html = entrada.description
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [
            p.get_text(separator=" ", strip=True)
            for p in s.find_all("p") + s.find_all("li")
        ]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)

def moncloa_parser(entrada: FeedParserDict) -> RSSEntrada:
    titulo = entrada.title
    autores = None
    link = entrada.link
    categorias = None
    from dateparser import parse

    fecha_publicacion = int(parse(entrada.published).timestamp())
    html = entrada.description
    from bs4 import BeautifulSoup

    s = BeautifulSoup(html, "html.parser")
    resumen = " \n".join(
        [
            p.get_text(separator=" ", strip=True)
            for p in s.find_all("p") + s.find_all("li")
        ]
    )
    return RSSEntrada(titulo, autores, link, categorias, fecha_publicacion, resumen)

parsers: dict[str, Callable[[FeedParserDict], RSSEntrada]] = {
    "el_pais": elpais_parser,
    "abc": abc_parser,
    "bbc": bbc_parser,
    "rtve_noticias": rtve_noticias_parser,
    "elconfidencial_mundo": elconfidencial_mundo_parser,
    "marca_primera_division": marca_primera_division_parser,
    "esdiario": esdiario_parser,
    "antena3": antena3_parser,
    "ministerio_dsa": ministerio_dsa_parser,
    "ministerio_eco": ministerio_eco_parser,
    "moncloa": moncloa_parser
}


__all__ = ["parsers", "RSSEntrada"]
