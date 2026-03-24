from .RSSParser import RSSParser


class BBCParser(RSSParser):
    def resumen(self) -> str:
        return self._entrada.description


__all__ = ["BBCParser"]
