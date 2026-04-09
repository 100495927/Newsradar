from mongo.Database import Database
from rss.links_estandar import generar_lista_estandar_feeds


def initializer() -> None:
    db = Database()
    feeds = generar_lista_estandar_feeds()
    for feed in feeds.feeds:
        db.col_rss_fuentes.insertar(feed)

    with open("/tmp/inicializado", "w") as f:
        f.write("ready")

def handler():
    from time import sleep
    # Para tareas de mantenimiento
    while True:
        sleep(10000)


if __name__ == "__main__":
    initializer()