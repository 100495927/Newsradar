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
    categorias: list[str] | None
    categorias_raw: list[str] | None
    fecha_publicacion: int  # Unix timestamp
    resumen: str | None = None

    def __str__(self) -> str:
        return f"""
        {self.titulo}
        {self.autores}
        {self.link}
        {self.categorias}
        {datetime.fromtimestamp(self.fecha_publicacion).strftime('%H:%M %d/%m/%Y')}
        """

    def a_mongo(self) -> dict:
        from datetime import datetime, timezone

        return {
            "titulo": self.titulo,
            "autores": self.autores,
            "link": self.link,
            "categorias": self.categorias,
            "categorias_raw": self.categorias_raw,
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
