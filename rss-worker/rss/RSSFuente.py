from __future__ import annotations

import hashlib
from typing import Type
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
    ):
        from .parsers import url_a_parser

        self.medio = medio
        self.rss = rss
        self.url = url
        self.parser = url_a_parser(url)
        self.activo = activo
        self.mongo_id = mongo_id
        self.category_id = category_id

    def obtener_entradas(self) -> list[RSSEntrada]:
        entradas = parse(self.url).entries
        entradas_parseadas = []
        for entrada in entradas:
            p = self.parser(entrada)
            entrada_parseada = p.generar(self)
            entradas_parseadas.append(entrada_parseada)

        return entradas_parseadas

    def a_mongo(self) -> dict:
        from datetime import datetime, timezone

        return {
            "hash_fuente": self.hash,
            "medio": self.medio,
            "rss": self.rss,
            "url": self.url,
            "tipo": "channel",
            "activo": self.activo,
            "category_id": self.category_id,
            "creado": datetime.now(timezone.utc),
            "actualizado": datetime.now(timezone.utc),
        }

    @classmethod
    def de_mongo(cls, mongo_dict: dict) -> "RSSFuente":

        try:
            medio = mongo_dict["medio"]
            rss = mongo_dict["rss"]
            url = mongo_dict["url"]
            activo = mongo_dict["activo"]
        except KeyError:
            raise KeyError("Dicionario de mongo no contiene los campos adecuados")
        return cls(
            medio=medio,
            rss=rss,
            url=url,
            activo=activo,
            mongo_id=mongo_dict.get("_id"),
            category_id=mongo_dict.get("category_id"),
        )

    @property
    def hash(self):
        h = (self.medio + self.rss).encode("utf-8")
        return hashlib.sha256(h).hexdigest()


__all__ = ["RSSFuente"]
