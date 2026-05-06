from __future__ import annotations

from shared.mongo.colecciones.ColeccionRssChannels import ColeccionRssChannels


class FakeCollection:
    def __init__(self, docs: list[dict]) -> None:
        self.docs = list(docs)

    def find(self, query: dict | None = None):
        query = query or {}
        return [doc for doc in self.docs if _matches(doc, query)]


def _matches(doc: dict, query: dict) -> bool:
    for key, value in query.items():
        if isinstance(value, dict) and "$exists" in value:
            exists = key in doc
            if exists != bool(value["$exists"]):
                return False
            continue
        if doc.get(key) != value:
            return False
    return True


class FakeDb:
    def __init__(self, source_docs: list[dict], channel_docs: list[dict]) -> None:
        self.col_information_sources = type(
            "FakeInformationSources",
            (),
            {"_collection": FakeCollection(source_docs)},
        )()
        self.db_app = {
            ColeccionRssChannels.NOMBRE_COLECCION: FakeCollection(channel_docs),
        }


def test_lista_canales_activos_devuelve_solo_canales_con_fuente_activa() -> None:
    db = FakeDb(
        source_docs=[
            {
                "id": 1,
                "name": "El Pais",
                "url": "https://elpais.com",
                "active": True,
            },
            {
                "id": 2,
                "name": "Fuente borrada",
                "url": "https://old.example.com",
                "active": False,
            },
        ],
        channel_docs=[
            {
                "id": 101,
                "information_source_id": 1,
                "url": "https://elpais.com/rss/politica.xml",
                "category_id": 11000000,
                "active": True,
            },
            {
                "id": 102,
                "information_source_id": 2,
                "url": "https://old.example.com/rss.xml",
                "category_id": 11000000,
                "active": True,
            },
            {
                "id": 103,
                "information_source_id": 999,
                "url": "https://missing.example.com/rss.xml",
                "category_id": 11000000,
                "active": True,
            },
            {
                "id": 104,
                "information_source_id": 1,
                "url": "https://elpais.com/rss/inactive.xml",
                "category_id": 11000000,
                "active": False,
            },
        ],
    )

    channels = ColeccionRssChannels(db).lista_canales_activos()

    assert len(channels) == 1
    assert channels[0].medio == "El Pais"
    assert channels[0].source_id == 1
    assert channels[0].channel_id == 101
    assert channels[0].source_url == "https://elpais.com"
    assert channels[0].url == "https://elpais.com/rss/politica.xml"
