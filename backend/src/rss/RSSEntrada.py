from dataclasses import dataclass
from datetime import datetime


@dataclass
class RSSEntrada:
    titulo: str
    autores: list[str]
    link: str
    categorias: list[str]
    fecha_publicacion: int  # Unix timestamp
    resumen: str

    def __str__(self) -> str:
        return f"""
        {self.titulo}
        {self.autores}
        {self.link}
        {self.categorias}
        {datetime.fromtimestamp(self.fecha_publicacion).strftime('%H:%M %d/%m/%Y')}
        {self.resumen}
        """


__all__ = ["RSSEntrada"]
