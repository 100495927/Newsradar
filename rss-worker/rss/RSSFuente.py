from __future__ import annotations

from feedparser import parse

from .RSSEntrada import RSSEntrada


class RSSFuente:
    # Fuente RSS

    def __init__(
        self,
        medio: str,
        rss: str,
        url: str,
        activo: bool = True,
        mongo_id: str | None = None,
        category_id: int | None = None,
        source_id: int | None = None,
        channel_id: int | None = None,
        source_url: str | None = None,
    ):
        from .parsers import url_a_parser

        self.medio = medio
        self.rss = rss
        self.url = url
        self.parser = url_a_parser(url)
        self.activo = activo
        self.mongo_id = mongo_id
        self.category_id = category_id
        self.source_id = source_id
        self.channel_id = channel_id
        self.source_url = source_url

    def obtener_entradas(self) -> list[RSSEntrada]:
        entradas = parse(self.url).entries
        entradas_parseadas = []
        for entrada in entradas:
            p = self.parser(entrada)
            entrada_parseada = p.generar(self)
            entradas_parseadas.append(entrada_parseada)

        return entradas_parseadas


__all__ = ["RSSFuente"]
