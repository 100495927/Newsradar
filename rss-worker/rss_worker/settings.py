from __future__ import annotations

from dataclasses import dataclass
from os import environ


@dataclass
class RssWorkerSettings:
    intervalo_rss: int
    rss_run_once: bool

    @classmethod
    def from_env(cls) -> "RssWorkerSettings":
        intervalo_rss = environ.get("RSS_WORKER_INTERVAL_SECONDS", "300")
        rss_run_once = environ.get("RSS_WORKER_RUN_ONCE", "false")

        if not intervalo_rss:
            raise ValueError("Intervalo RSS no encontrado")
        if not rss_run_once:
            raise ValueError("RSS run once no encontrado")
        if not intervalo_rss.isdigit():
            raise ValueError("Intervalo RSS invalido")

        return cls(
            intervalo_rss=int(intervalo_rss),
            rss_run_once=rss_run_once.strip().lower() == "true",
        )
