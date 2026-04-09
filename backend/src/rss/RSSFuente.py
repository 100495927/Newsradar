from typing import Type
from rss.parsers import RSSParser
from rss.RSSEntrada import RSSEntrada
import hashlib


class RSSFuente:
    # Fuente RSS

    def __init__(
        self,
        medio: str,
        rss: str,
        url: str,
        parser: Type[RSSParser],
        activo: bool = True,
        mongo_id: str | None = None
    ):
        self.medio = medio
        self.rss = rss
        self.url = url
        self.parser = parser
        self.activo = activo

    def obtener_entradas(self) -> list[RSSEntrada]:
        from feedparser import parse

        entradas = parse(self.url).entries
        entradas_parseadas = []
        for entrada in entradas:
            p = self.parser(entrada)
            entrada_parseada = p.generar(self)
            entradas_parseadas.append(entrada_parseada)

        return entradas_parseadas

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

    @classmethod
    def de_mongo(cls, mongo_dict: dict) -> 'RSSFuente':
        from .parsers.mongo_ids import mongo_parser_ids

        try:
            hash_fuente = mongo_dict["hash_fuente"]
            medio = mongo_dict["medio"]
            rss = mongo_dict["rss"]
            url = mongo_dict["url"]
            parser_id = mongo_dict["parser_id"]
            activo = mongo_dict["activo"]
            creado = mongo_dict["creado"]
            actualizado = mongo_dict["actualizado"]
        except KeyError:
            raise KeyError("Dicionario de mongo no contiene los campos adecuados")
        return RSSFuente(
            medio=medio,
            rss=rss,
            url=url,
            parser=mongo_parser_ids[parser_id],
            activo=activo
        )

    @property
    def hash(self):
        h = (self.medio + self.rss + self.url).encode("utf-8")
        return hashlib.sha256(h).hexdigest()


__all__ = ["RSSFuente"]
