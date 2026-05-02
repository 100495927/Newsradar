from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from shared.mongo.colecciones.ColeccionRssEntradas import ColeccionRssEntradas


class FakeEntradasCollection:
    def __init__(self) -> None:
        self.last_update = None

    def update_one(self, filter_doc, update_doc, upsert=False):
        self.last_update = (filter_doc, update_doc, upsert)
        return SimpleNamespace(upserted_id=None)


class FakeFuentesCollection:
    def find_one(self, query):
        return {"_id": "fuente-id"}


class FakeDatabase:
    def __init__(self, entradas_collection: FakeEntradasCollection) -> None:
        self._db_app = {
            ColeccionRssEntradas.NOMBRE_COLECCION: entradas_collection,
        }
        self.col_rss_fuentes = SimpleNamespace(_collection=FakeFuentesCollection())

    @property
    def db_app(self):
        return self._db_app


def test_insertar_preserva_fecha_ingestion_original_en_duplicados() -> None:
    entradas_collection = FakeEntradasCollection()
    collection = ColeccionRssEntradas(FakeDatabase(entradas_collection))
    fecha_ingestion_original = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    entrada = SimpleNamespace(
        fuente=SimpleNamespace(url="https://example.com/feed.xml"),
        a_mongo=lambda: {
            "titulo": "Titulo",
            "autores": ["Autor"],
            "link": "https://example.com/noticia",
            "category_id": 1000000,
            "resumen": "Resumen",
            "fecha_publicacion": datetime(2026, 5, 1, 11, 0, tzinfo=timezone.utc),
            "hash_deduplicado": "hash",
            "fecha_ingestion": fecha_ingestion_original,
        },
    )

    collection.insertar(entrada)

    _, update_doc, upsert = entradas_collection.last_update
    assert upsert is True
    assert update_doc["$setOnInsert"]["fecha_ingestion"] == fecha_ingestion_original
    assert "$set" not in update_doc
