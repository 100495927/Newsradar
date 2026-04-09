from mongo import Database
from Entorno import Entorno
from time import sleep
from rss.links_estandar import generar_lista_estandar_feeds
from rss.RSSFuente import RSSFuente
from rss.RSSEntrada import RSSEntrada


def main() -> None:
    entorno = Entorno()
    db = Database()
    feeds = generar_lista_estandar_feeds()
    for feed in feeds:
        db.col_rss_fuentes.insertar(feed)
    print("2")
    if entorno.run_once == "true":
        print("3")
        fetch_de_entradas(db)
    else:
        while True:
            print("4")
            fetch_de_entradas(db)
            sleep(float(entorno.intervalo_rss))


def fetch_de_entradas(db: Database):
    fuentes: list[RSSEntrada] = db.col_rss_fuentes.lista_fuentes()
    print(fuentes)
    for fuente in fuentes:
        entradas = fuente.obtener_entradas()
        for entrada in entradas:
            print(entrada)
            db.col_rss_entradas.insertar(entrada)


if __name__ == "__main__":
    print("1")
    main()
