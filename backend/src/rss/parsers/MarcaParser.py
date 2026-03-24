from .RSSParser import RSSParser


class MarcaParser(RSSParser):
    def resumen(self) -> str:
        html = self._entrada.description
        from bs4 import BeautifulSoup

        s = BeautifulSoup(html, "html.parser")
        resumen = s.get_text(separator=" ", strip=False)

        return resumen


__all__ = ["MarcaParser"]
