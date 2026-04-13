from time import sleep

from shared.mongo import Database


def initializer() -> None:
    Database()


def handler() -> None:
    # Para tareas de mantenimiento
    while True:
        sleep(10000)


if __name__ == "__main__":
    initializer()
    handler()
