import os
import json
import requests
import feedparser
from pathlib import Path
from dataclasses import dataclass
from parser import RSSEntrada, parsers
from typing import Callable


class RSSFeedList:
    # Lista de fuentes
    def __init__(
        self, parsers: dict[str, Callable[[feedparser.FeedParserDict], RSSEntrada]]
    ):
        self._feeds: list[RSSFeedSource] = []
        self._parsers = parsers

    def añadir(self, nombre, url):
        if nombre not in self._parsers.keys():
            raise ValueError("La fuente dada no tiene un parser asociado")
        feed = RSSFeedSource(nombre, url, self._parsers[nombre])
        self._feeds.append(feed)

    def __iter__(self):
        yield from self._feeds

    def obtener_url(self, nombre):
        for i in self:
            i: RSSFeedSource
            if i.nombre == nombre:
                return i.url


class RSSFeed:
    # RSS
    def __init__(self, fuente, titulo, link, entradas):
        self._fuente = fuente
        self._titulo = titulo
        self._link = link
        self._entradas = []

        for entrada in entradas:
            entrada_parseada = self._fuente.parser(entrada)
            self._entradas.append(entrada_parseada)

    def __str__(self):
        return f"""
        {self._titulo}
        {self._link}
        """

    def __iter__(self):
        yield from self.entradas

    @property
    def entradas(self):
        yield from self._entradas


class RSSFeedSource:
    # Fuente RSS
    nombre: str
    url: str
    parser: Callable[[feedparser.FeedParserDict], RSSEntrada]

    def __init__(
        self,
        nombre: str,
        url: str,
        parser: Callable[[feedparser.FeedParserDict], RSSEntrada],
    ):
        self.nombre = nombre
        self.url = url
        self.parser = parser

    def obtener_entradas(self) -> RSSFeed:
        feed = feedparser.parse(self.url)
        objeto_feed = RSSFeed(self, feed.feed.title, feed.feed.link, feed.entries)
        return objeto_feed


if __name__ == "__main__":
    # Pruebas
    feeds = RSSFeedList(parsers)
    """feeds.añadir(
        "el_pais", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
    )
    feeds.añadir("abc", "https://www.abc.es/rss/feeds/abcPortada.xml")
    feeds.añadir("bbc", "https://feeds.bbci.co.uk/news/world/rss.xml")
    feeds.añadir("rtve_noticias", "https://api2.rtve.es/rss/temas_noticias.xml")
    feeds.añadir("elconfidencial_mundo", "https://rss.elconfidencial.com/mundo/")
    feeds.añadir("marca_primera_division", "https://objetos.estaticos-marca.com/rss/futbol/primera-division.xml")
    feeds.añadir("esdiario", "https://www.esdiario.com/rss/home.xml")
    feeds.añadir("antena3", "https://www.antena3.com/noticias/rss/4013050.xml")
    feeds.añadir("ministerio_dsa", "https://www.dsca.gob.es/es/rss-noticias.xml")"""
    feeds.añadir("moncloa", "https://www.lamoncloa.gob.es/paginas/rss.aspx")
    for feed in feeds:
        f = feed.obtener_entradas()
        print(f)
        for entrada in f:
            print(f"{entrada}\n\n")
