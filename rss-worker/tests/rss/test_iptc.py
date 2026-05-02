from rss.RSSFuente import RSSFuente
from rss.parsers.RSSParser import RSSParser


class DummyEntry(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc


def test_parser_inherits_category_id_from_source() -> None:
    entry = DummyEntry(
        title="Titulo",
        link="https://example.com/noticia",
        summary="Resumen",
        published_parsed=(2026, 4, 19, 12, 0, 0, 0, 0, 0),
    )
    parser = RSSParser(entry)
    fuente = RSSFuente(
        "hispasec",
        "una_al_dia",
        "https://feeds.feedburner.com/hispasec/zCAd",
        category_id=13000000,
    )

    noticia = parser.generar(fuente)

    assert noticia.category_id == 13000000
