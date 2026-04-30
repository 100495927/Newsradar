from feedparser import FeedParserDict

from ..RSSEntrada import RSSEntrada
from ..RSSFuente import RSSFuente


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

    def resumen(self) -> str | None:
        texto = self._entrada.get("summary") or self._entrada.get("description")
        if not texto:
            return None
        return str(texto)

    def categorias(self) -> list[str] | None:
        cat = [tag.term for tag in self._entrada.get("tags", [])]
        if len(cat) == 0:
            return None
        return cat

    def fecha_publicacion(self) -> int:
        from calendar import timegm

        return timegm(self._entrada.published_parsed)

    def generar(self, fuente: RSSFuente) -> RSSEntrada:
        categorias_raw = self.categorias()
        return RSSEntrada(
            fuente,
            self.titulo(),
            self.autores(),
            self.link(),
            None,
            categorias_raw,
            self.fecha_publicacion(),
            self.resumen(),
        )


__all__ = ["RSSParser"]
