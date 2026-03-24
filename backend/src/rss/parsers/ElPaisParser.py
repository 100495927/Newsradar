from .RSSParser import RSSParser


class ElPaisParser(RSSParser):
    def resumen(self) -> str:
        for c in self._entrada.content:
            if c.type == "text/html" or c.type == "html":
                html = c.value

        from bs4 import BeautifulSoup

        s = BeautifulSoup(html, "html.parser")
        resumen = " \n".join(
            [
                p.get_text(separator=" ", strip=True)
                for p in s.find_all("p") + s.find_all("li")
            ]
        )
        return resumen


__all__ = ["ElPaisParser"]
