from rss.RSSFuente import RSSFuente
from rss.iptc import canonicalize_iptc_category, normalize_feed_categories
from rss.parsers.RSSParser import RSSParser


class DummyTag:
    def __init__(self, term: str):
        self.term = term


class DummyEntry(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc


def test_canonicalize_exact_iptc_category() -> None:
    assert canonicalize_iptc_category("Política") == "Política"


def test_canonicalize_alias_to_top_level() -> None:
    assert canonicalize_iptc_category("Phishing") == "Ciencia y tecnología"


def test_normalize_feed_categories_uses_fallback_when_raw_tags_are_not_iptc() -> None:
    categorias, categorias_raw = normalize_feed_categories(
        ["General"],
        "Política",
    )

    assert categorias == ["Política"]
    assert categorias_raw == ["General"]


def test_parser_stores_raw_categories_and_normalized_iptc_categories() -> None:
    entry = DummyEntry(
        title="Titulo",
        link="https://example.com/noticia",
        summary="Resumen",
        published_parsed=(2026, 4, 19, 12, 0, 0, 0, 0, 0),
        tags=[DummyTag("Phishing"), DummyTag("General")],
    )
    parser = RSSParser(entry)
    fuente = RSSFuente(
        "hispasec",
        "una_al_dia",
        "https://feeds.feedburner.com/hispasec/zCAd",
        categoria_iptc="Ciencia y tecnología",
    )

    noticia = parser.generar(fuente)

    assert noticia.categorias == ["Ciencia y tecnología"]
    assert noticia.categorias_raw == ["Phishing", "General"]
