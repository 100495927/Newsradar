from alerts import deliver_pending_notifications
from rss.links_estandar import generar_lista_estandar_feeds
from alerts import process_alerts
from alerts import process_due_alerts
from alert_worker.main import main as alert_worker_main
from alert_worker.settings import AlertWorkerSettings
from rss_worker.main import fetch_de_entradas
from rss_worker.main import main as rss_worker_main
from rss_worker.settings import RssWorkerSettings


def test_generar_lista_estandar_feeds_devuelve_fuentes() -> None:
    feeds = generar_lista_estandar_feeds()

    assert feeds
    assert all(feed.url for feed in feeds)


def test_worker_main_expone_fetch_de_entradas() -> None:
    assert callable(fetch_de_entradas)
    assert callable(rss_worker_main)
    assert callable(alert_worker_main)


def test_workers_exponen_settings_separados() -> None:
    assert callable(RssWorkerSettings.from_env)
    assert callable(AlertWorkerSettings.from_env)


def test_worker_expone_procesador_de_alertas() -> None:
    assert callable(process_alerts)
    assert callable(process_due_alerts)
    assert callable(deliver_pending_notifications)
