from dataclasses import dataclass
from datetime import datetime


@dataclass
class RSSEntrada:
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

    def __dict__(self) -> dict:
        return {
            "titulo": self.titulo,
            "autores": self.autores,
            "link": self.link,
            "categorias": self.categorias,
            "fecha_publicacion": self.fecha_publicacion,
        }


__all__ = ["RSSEntrada"]
