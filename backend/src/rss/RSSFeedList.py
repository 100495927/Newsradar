from rss.parsers import RSSParser
from rss.RSSFeedSource import RSSFeedSource
from typing import Type


class RSSFeedList:
    # Lista de fuentes
    def __init__(self):
        self._feeds: list[RSSFeedSource] = []

    def añadir(self, medio, rss, url, parser: Type[RSSParser]):
        feed = RSSFeedSource(medio, rss, url, parser)
        self._feeds.append(feed)

    @property
    def feeds(self):
        return tuple(self._feeds)


__all__ = ["RSSFeedList"]
