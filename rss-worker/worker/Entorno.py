from __future__ import annotations

from alert_worker.settings import AlertWorkerSettings
from rss_worker.settings import RssWorkerSettings


class Entorno:
    """Capa de compatibilidad legacy sobre los settings separados."""

    def __init__(self):
        self._rss = RssWorkerSettings.from_env()
        self._alerts = AlertWorkerSettings.from_env()

    @property
    def intervalo_rss(self):
        return self._rss.intervalo_rss

    @property
    def run_once(self):
        return self._rss.run_once

    @property
    def puerto_uvicorn(self):
        return self._rss.puerto_uvicorn

    @property
    def intervalo_alertas(self):
        return self._alerts.intervalo_alertas

    @property
    def alert_run_once(self):
        return self._alerts.alert_run_once


__all__ = ["Entorno"]
