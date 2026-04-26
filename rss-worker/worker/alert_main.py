from __future__ import annotations

import logging
from time import sleep

from alerts import deliver_pending_notifications, process_due_alerts
from shared.mongo.Database import Database
from worker.Entorno import Entorno
from worker.main import run_preflight

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[alert-worker] %(asctime)s %(levelname)s %(message)s",
    )


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
    configure_logging()
    entorno = Entorno()
    db = Database()
    run_preflight(db)

    if entorno.alert_run_once == "true":
        process_due_alerts_safely(db)
        deliver_pending_notifications_safely(db)
        return

    while True:
        try:
            process_due_alerts_safely(db)
            deliver_pending_notifications_safely(db)
        except Exception:
            logger.exception("Fallo un ciclo completo de alert-worker")
        sleep(float(entorno.intervalo_alertas))


if __name__ == "__main__":
    main()
