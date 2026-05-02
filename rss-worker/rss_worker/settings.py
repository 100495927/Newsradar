from __future__ import annotations

from dataclasses import dataclass
from os import environ


@dataclass
class RssWorkerSettings:
    intervalo_rss: str
    rss_run_once: str
    uvicorn_port: str

    @classmethod
    def from_env(cls) -> "RssWorkerSettings":
        intervalo_rss = environ.get("RSS_WORKER_INTERVAL_SECONDS", "300")
        rss_run_once = environ.get("RSS_WORKER_RUN_ONCE", "false")
        uvicorn_port = environ.get("RSS_WORKER_UVICORN_PORT", "8000")

        if not intervalo_rss:
            raise ValueError("Intervalo RSS no encontrado")
        if not rss_run_once:
            raise ValueError("RSS run once no encontrado")
        if not uvicorn_port:
            raise ValueError("Puerto uvicorn RSS no encontrado")

        return cls(
            intervalo_rss=intervalo_rss,
            rss_run_once=rss_run_once,
            uvicorn_port=uvicorn_port,
        )
