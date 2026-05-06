from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .RSSFuente import RSSFuente


@dataclass
class RSSEntrada:
    fuente: "RSSFuente"
    titulo: str
    autores: list[str] | None
    link: str
    category_id: int | None
    fecha_publicacion: int  # Unix timestamp
    resumen: str | None = None

    def __str__(self) -> str:
        return f"""
        {self.titulo}
        {self.autores}
        {self.link}
        {self.category_id}
        {datetime.fromtimestamp(self.fecha_publicacion).strftime('%H:%M %d/%m/%Y')}
        """

    def a_mongo(self) -> dict:
        from datetime import datetime, timezone

        return {
            "information_source_id": self.fuente.source_id,
            "rss_channel_id": self.fuente.channel_id,
            "source_name": self.fuente.medio,
            "source_url": self.fuente.source_url,
            "channel_url": self.fuente.url,
            "titulo": self.titulo,
            "autores": self.autores,
            "link": self.link,
            "category_id": self.category_id,
            "resumen": self.resumen,
            "fecha_publicacion": datetime.fromtimestamp(
                self.fecha_publicacion, tz=timezone.utc
            ),
            "hash_deduplicado": self.hash,
            "fecha_ingestion": datetime.now(timezone.utc),
        }

    @property
    def hash(self):
        import hashlib

        h = (self.link + self.titulo).encode("utf-8")
        return hashlib.sha256(h).hexdigest()


__all__ = ["RSSEntrada"]
