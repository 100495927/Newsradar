from mongo import Database
from Entorno import Entorno
from time import sleep
from rss.links_estandar import generar_lista_estandar_feeds
from rss.RSSFeedList import RSSFeedList


def main() -> None:
    entorno = Entorno()
    db = Database()
    feeds = generar_lista_estandar_feeds()
    for feed in feeds.feeds:
        db.col_rss_fuentes.insertar(feed)

    if entorno.run_once == "true":
        fetch_de_entradas(db)
    else:
        while True:
            fetch_de_entradas(db)
            sleep(entorno.intervalo_rss)


def fetch_de_entradas(db: Database):
    fuentes: RSSFeedList = db.col_rss_fuentes.lista_fuentes()
    for fuente in fuentes.feeds:
        entradas = feed.obtener_entradas()
        db.col_rss_fuentes.insertar(feed)
        for entrada in entradas.entradas:
            db.col_rss_entradas.insertar(entrada)


if __name__ == "__main__":
    main()
