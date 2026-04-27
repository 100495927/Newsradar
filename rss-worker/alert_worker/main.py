from __future__ import annotations

import logging
from time import sleep

from alerts import deliver_pending_notifications, process_due_alerts
from alert_worker.settings import AlertWorkerSettings
from runtime_common import configure_logging
from shared.mongo.Database import Database

logger = logging.getLogger(__name__)


def process_due_alerts_safely(db: Database) -> int:
    try:
        return process_due_alerts(db)
    except Exception:
        logger.exception("Fallo el procesamiento programado de alertas")
        return 0


def deliver_pending_notifications_safely(db: Database) -> int:
    try:
        return deliver_pending_notifications(db)
    except Exception:
        logger.exception("Fallo la entrega programada de notificaciones pendientes")
        return 0


def main() -> None:
    configure_logging("alert-worker")
    settings = AlertWorkerSettings.from_env()
    db = Database()

    if settings.alert_run_once == "true":
        process_due_alerts_safely(db)
        deliver_pending_notifications_safely(db)
        return

    while True:
        try:
            process_due_alerts_safely(db)
            deliver_pending_notifications_safely(db)
        except Exception:
            logger.exception("Fallo un ciclo completo de alert-worker")
        sleep(float(settings.intervalo_alertas))


if __name__ == "__main__":
    main()
