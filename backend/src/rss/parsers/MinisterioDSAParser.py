from .RSSParser import RSSParser


class MinisterioDSAParser(RSSParser):
    def fecha_publicacion(self) -> int:
        from dateparser import parse

        return int(parse(self._entrada.published).timestamp())


__all__ = ["MinisterioDSAParser"]
