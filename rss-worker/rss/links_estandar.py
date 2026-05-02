from .RSSFuente import RSSFuente
from shared.rss_seed_sources import STANDARD_RSS_SOURCES

def generar_lista_estandar_feeds() -> list[RSSFuente]:
    return [
        RSSFuente(
            medio=source.medio,
            rss=source.rss,
            url=source.url,
            activo=source.activo,
            category_id=source.category_id,
        )
        for source in STANDARD_RSS_SOURCES
    ]

__all__ = ["generar_lista_estandar_feeds"]
