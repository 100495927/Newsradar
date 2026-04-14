from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .Coleccion import Coleccion

if TYPE_CHECKING:
    from rss.RSSEntrada import RSSEntrada


class ColeccionRssEntradas(Coleccion):
    NOMBRE_COLECCION = "rss_entradas"

    def insertar(self, entrada: "RSSEntrada"):
        datos = entrada.a_mongo()
        url_fuente = entrada.fuente.url

        id_fuente = self._db_padre.col_rss_fuentes._collection.find_one({"url": url_fuente})
        if not id_fuente:
            raise ValueError(f"No se encontró la fuente en la BD para la URL: {url_fuente}")
        datos["id_fuente"] = id_fuente["_id"]
        datos.pop("fecha_ingestion")
        resultado = self._collection.update_one(
            {"hash_deduplicado": datos["hash_deduplicado"]},
            {
                "$setOnInsert": datos,
                "$set": {"fecha_ingestion": datetime.now(timezone.utc)},
            },
            upsert=True,
        )
        return resultado.upserted_id
