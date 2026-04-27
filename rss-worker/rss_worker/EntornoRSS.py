from dataclasses import dataclass
from os import environ


@dataclass
class EntornoRSS:
    VARENV_INTERVALO_RSS = "RSS_WORKER_INTERVAL_SECONDS"
    VARENV_RUN_ONCE = "RSS_WORKER_RUN_ONCE"
    VARENV_PUERTO_UVICORN = "RSS_WORKER_UVICORN_PORT"
    DEFAULT_INTERVALO_RSS = "60"
    DEFAULT_RUN_ONCE = "false"
    DEFAULT_PUERTO_UVICORN = "8000"

    def __init__(self):
        self.__intervalo_rss = environ.get(
            self.VARENV_INTERVALO_RSS,
            self.DEFAULT_INTERVALO_RSS,
        )
        self.__run_once = environ.get(self.VARENV_RUN_ONCE, self.DEFAULT_RUN_ONCE)
        self.__uvicorn_port = environ.get(
            self.VARENV_PUERTO_UVICORN,
            self.DEFAULT_PUERTO_UVICORN,
        )

    @property
    def intervalo_rss(self) -> int:
        if not self.__intervalo_rss:
            raise ValueError("Intervalo de rss no encontrado")
        if not self.__intervalo_rss.isdigit():
            raise TypeError("Intervalo de rss no es un numero")
        return int(self.__intervalo_rss)

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

__all__ = ["EntornoRSS"]
