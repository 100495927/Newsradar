from dataclasses import dataclass
from datetime import datetime
from rss.RSSFeedSource import RSSFeedSource

@dataclass
class RSSEntrada:
    fuente: RSSFeedSource
    titulo: str
    autores: list[str]
    link: str
    categorias: list[str]
    fecha_publicacion: int  # Unix timestamp

    def __str__(self) -> str:
        return f"""
        {self.titulo}
        {self.autores}
        {self.link}
        {self.categorias}
        {datetime.fromtimestamp(self.fecha_publicacion).strftime('%H:%M %d/%m/%Y')}
        """

    def a_mongo(self) -> dict:
        from time import time
        from datetime import datetime, timezone
        return {
            "id_fuente": self.fuente.hash,
            "titulo": self.titulo,
            "autores": self.autores,
            "link": self.link,
            "categorias": self.categorias,
            "fecha_publicacion": datetime.fromtimestamp(self.fecha_publicacion, tz=timezone.utc),
            "hash_deduplicado": self.hash,
            "fecha_ingestion": datetime.now(timezone.utc)
        }
    
    @property
    def hash(self):
        import hashlib
        h = (self.link + self.titulo).encode('utf-8')
        return hashlib.sha256(h).hexdigest()


__all__ = ["RSSEntrada"]
