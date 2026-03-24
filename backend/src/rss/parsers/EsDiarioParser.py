from .RSSParser import RSSParser


class EsDiarioParser(RSSParser):
    def resumen(self) -> str:
        html = self._entrada.content[0].value
        from bs4 import BeautifulSoup

        s = BeautifulSoup(html, "html.parser")
        resumen = " \n".join(
            [p.get_text(separator=" ", strip=True) for p in s.find_all("p")]
        )
        return resumen


__all__ = ["EsDiarioParser"]
