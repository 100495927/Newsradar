from dataclasses import dataclass
from os import environ


@dataclass
class Entorno:
    VARENV_INTERVALO_RSS = "RSS_WORKER_INTERVAL_SECONDS"
    VARENV_RUN_ONCE = "RSS_WORKER_RUN_ONCE"
    VARENV_PUERTO_UVICORN = "RSS_WORKER_UVICORN_PORT"

    def __init__(self):
        self.__intervalo_rss = environ.get(self.VARENV_INTERVALO_RSS)
        if not self.__intervalo_rss:
            raise ValueError(
                f"Variable de entorno {self.VARENV_INTERVALO_RSS} no encontrada"
            )
        self.__run_once = environ.get(self.VARENV_RUN_ONCE)
        if not self.__run_once:
            raise ValueError(f"Variable de entorno {self.VARENV_RUN_ONCE} no encontrada")
        self.__uvicorn_port = environ.get(self.VARENV_PUERTO_UVICORN)
        if not self.__uvicorn_port:
            raise ValueError(f"Variable de entorno {self.VARENV_PUERTO_UVICORN} no encontrada")

    @property
    def intervalo_rss(self):
        if not self.__intervalo_rss:
            raise ValueError("Intervalo de rss no encontrado")
        return self.__intervalo_rss

    @property
    def run_once(self):
        if not self.__run_once:
            raise ValueError("Run once no encontrado")
        return self.__run_once

    @property
    def puerto_uvicorn(self):
        if not self.__uvicorn_port:
            raise ValueError("Puerto de uvicorn no encontrado")
        return int(self.__uvicorn_port)

__all__ = ["Entorno"]
