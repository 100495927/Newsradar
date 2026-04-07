from mongo import Database
from .Entorno import Entorno


def main() -> None:
    entorno = Entorno()
    db = Database()

    fuentes: RSSFeedList = db.col_rss_fuentes.lista_fuentes()
    for fuente in fuentes.feeds:
        entradas = feed.obtener_entradas()
        db.col_rss_fuentes.insertar(feed)
        for entrada in entradas.entradas:
            db.col_rss_entradas.insertar(entrada)


if __name__ == "__main__":
    pass
