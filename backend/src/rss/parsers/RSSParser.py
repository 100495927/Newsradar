from rss.RSSEntrada import RSSEntrada
from feedparser import FeedParserDict


class RSSParser:
    def __init__(self, entrada: FeedParserDict):
        self._entrada: FeedParserDict = entrada

    def titulo(self) -> str:
        return self._entrada.title

    def autores(self) -> list[str] | None:
        if hasattr(self._entrada, "authors"):
            a: list[dict] = self._entrada.authors
            if len(a) == 0:
                return None
            if len(a[0]) == 0:
                return None
            return [autor["name"] for autor in a]
        return None

    def link(self) -> str:
        return self._entrada.link

    def categorias(self) -> list[str]:
        cat = [tag.term for tag in self._entrada.get("tags", [])]
        if len(cat) == 0:
            return None
        return cat

    def fecha_publicacion(self) -> int:
        from calendar import timegm

        return timegm(self._entrada.published_parsed)

    def generar(self) -> RSSEntrada:
        return RSSEntrada(
            self.titulo(),
            self.autores(),
            self.link(),
            self.categorias(),
            self.fecha_publicacion(),
        )


__all__ = ["RSSParser"]
