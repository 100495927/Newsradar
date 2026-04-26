from __future__ import annotations

from dataclasses import dataclass
from os import environ


@dataclass
class RssWorkerSettings:
    intervalo_rss: str
    run_once: str
    puerto_uvicorn: int

    @classmethod
    def from_env(cls) -> "RssWorkerSettings":
        intervalo_rss = environ.get("RSS_WORKER_INTERVAL_SECONDS", "60")
        run_once = environ.get("RSS_WORKER_RUN_ONCE", "false")
        puerto_uvicorn = environ.get("RSS_WORKER_UVICORN_PORT", "8000")

        if not intervalo_rss:
            raise ValueError("Intervalo de rss no encontrado")
        if not run_once:
            raise ValueError("Run once no encontrado")
        if not puerto_uvicorn:
            raise ValueError("Puerto de uvicorn no encontrado")

        return cls(
            intervalo_rss=intervalo_rss,
            run_once=run_once,
            puerto_uvicorn=int(puerto_uvicorn),
        )
