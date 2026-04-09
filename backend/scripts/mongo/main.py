from mongo.Database import Database
from rss.links_estandar import generar_lista_estandar_feeds


def initializer() -> None:
    db = Database()


def handler():
    from time import sleep

    # Para tareas de mantenimiento
    while True:
        sleep(10000)


if __name__ == "__main__":
    initializer()
    handler()
