from typing import Type
from rss.parsers import RSSParser
from rss.RSSFeed import RSSFeed


class RSSFeedSource:
    # Fuente RSS
    nombre: str
    url: str
    parser: Type[RSSParser]

    def __init__(
        self,
        medio: str,
        rss: str,
        url: str,
        parser: Type[RSSParser],
    ):
        self.medio = medio
        self.rss = rss
        self.url = url
        self.parser = parser

    def obtener_entradas(self) -> RSSFeed:
        from feedparser import parse

        feed = parse(self.url)
        objeto_feed = RSSFeed(self, feed.feed.title, feed.feed.link, feed.entries)
        return objeto_feed


__all__ = ["RSSFeedSource"]
