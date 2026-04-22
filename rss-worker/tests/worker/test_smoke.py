from rss.links_estandar import generar_lista_estandar_feeds
from alerts import process_alerts
from worker.main import fetch_de_entradas
from worker.main import process_alerts_safely


def test_generar_lista_estandar_feeds_devuelve_fuentes() -> None:
    feeds = generar_lista_estandar_feeds()

    assert feeds
    assert all(feed.url for feed in feeds)


def test_worker_main_expone_fetch_de_entradas() -> None:
    assert callable(fetch_de_entradas)


def test_worker_expone_procesador_de_alertas() -> None:
    assert callable(process_alerts)
    assert callable(process_alerts_safely)
