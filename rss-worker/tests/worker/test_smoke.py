import rss_worker

from alert_worker.main import main as alert_worker_main
from alert_worker.settings import AlertWorkerSettings
from rss.links_estandar import generar_lista_estandar_feeds
from rss_worker.fetch_pipeline import fetch_de_entradas
from rss_worker.main import main as rss_worker_main
from rss_worker.settings import RssWorkerSettings


def test_generar_lista_estandar_feeds_devuelve_canales() -> None:
    feeds = generar_lista_estandar_feeds()

    assert len(feeds) == 100
    assert all(feed.url for feed in feeds)
    assert len({feed.url for feed in feeds}) == 100


def test_worker_main_expone_fetch_de_entradas() -> None:
    assert callable(fetch_de_entradas)
    assert callable(rss_worker_main)
    assert callable(alert_worker_main)


def test_workers_exponen_settings_separados() -> None:
    assert callable(RssWorkerSettings.from_env)
    assert callable(AlertWorkerSettings.from_env)


def test_rss_worker_no_expone_api_ni_alertas() -> None:
    assert not hasattr(rss_worker, "api_task")
