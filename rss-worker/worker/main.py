from __future__ import annotations

from time import sleep

from rss.links_estandar import generar_lista_estandar_feeds
from rss.RSSFuente import RSSFuente
from shared.mongo import Database
from worker.Entorno import Entorno


def main() -> None:
    entorno = Entorno()
    db = Database()
    for feed in generar_lista_estandar_feeds():
        db.col_rss_fuentes.insertar(feed)

    if entorno.run_once == "true":
        fetch_de_entradas(db)
        return

    while True:
        fetch_de_entradas(db)
        sleep(float(entorno.intervalo_rss))


def fetch_de_entradas(db: Database) -> None:
    fuentes: list[RSSFuente] = db.col_rss_fuentes.lista_fuentes()
    for fuente in fuentes:
        for entrada in fuente.obtener_entradas():
            db.col_rss_entradas.insertar(entrada)


if __name__ == "__main__":
    main()
