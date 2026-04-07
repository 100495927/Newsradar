from mongo.Database import Database
from rss.links_estandar import generar_lista_estandar_feeds


def main() -> None:
    db = Database()
    feeds = generar_lista_estandar_feeds()
    for feed in feeds.feeds:
        db.col_rss_fuentes.insertar(feed)


if __name__ == "__main__":
    main()
