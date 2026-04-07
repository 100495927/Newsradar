from dataclasses import dataclass
from os import environ
from .constantes.entorno import *


@dataclass
class Entorno:
    VARENV_INTERVALO_RSS = "RSS_WORKER_INTERVAL_SECONDS"
    VARENV_RUN_ONCE = "RSS_WORKER_RUN_ONCE"

    def __init__(self):
        self.__intervalo_rss = environ.get(VARENV_INTERVALO_RSS)
        if not self.__intervalo_rss:
            raise ValueError(
                f"Variable de entorno {VARENV_INTERVALO_RSS} no encontrada"
            )
        self.__run_once = environ.get(VARENV_RUN_ONCE)
        if not self.__run_once:
            raise ValueError(f"Variable de entorno {VARENV_RUN_ONCE} no encontrada")

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


__all__ = ["Entorno"]
