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

    def a_mongo(self) -> dict:
        from time import time
        from .parsers import mongo_parser_ids

        return {
            "medio": self.medio,
            "rss": self.rss,
            "url": self.url,
            "parser_id": mongo_parser_ids.inv[self.parser],
            "creado": int(time()),
            "actualizado": int(time()),
        }


__all__ = ["RSSFeedSource"]
