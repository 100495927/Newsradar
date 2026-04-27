from __future__ import annotations

from dataclasses import dataclass
from os import environ


@dataclass
class AlertWorkerSettings:
    intervalo_alertas: str
    alert_run_once: str

    @classmethod
    def from_env(cls) -> "AlertWorkerSettings":
        intervalo_alertas = environ.get("ALERT_WORKER_INTERVAL_SECONDS", "60")
        alert_run_once = environ.get("ALERT_WORKER_RUN_ONCE", "false")

        if not intervalo_alertas:
            raise ValueError("Intervalo de alertas no encontrado")
        if not alert_run_once:
            raise ValueError("Alert run once no encontrado")

        return cls(
            intervalo_alertas=intervalo_alertas,
            alert_run_once=alert_run_once,
        )
