from typing import Type
from rss.parsers import RSSParser
from rss.RSSFeed import RSSFeed
import hashlib


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
        activo: bool = True,
    ):
        self.medio = medio
        self.rss = rss
        self.url = url
        self.parser = parser
        self.activo = activo
        # Se rellena al persistir en Mongo para referenciar entradas con ObjectId.
        self.mongo_id = None

    def obtener_entradas(self) -> RSSFeed:
        from feedparser import parse

        feed = parse(self.url)
        objeto_feed = RSSFeed(self, feed.feed.title, feed.feed.link, feed.entries)
        return objeto_feed

    def a_mongo(self) -> dict:
        from datetime import datetime, timezone
        from .parsers import mongo_parser_ids

        return {
            "hash_fuente": self.hash,
            "medio": self.medio,
            "rss": self.rss,
            "url": self.url,
            "parser_id": mongo_parser_ids.inv[self.parser],
            "activo": self.activo,
            "creado": datetime.now(timezone.utc),
            "actualizado": datetime.now(timezone.utc),
        }

    @property
    def hash(self):
        h = (self.medio + self.rss + self.url).encode("utf-8")
        return hashlib.sha256(h).hexdigest()


__all__ = ["RSSFeedSource"]
