from shared.mongo import Database
from EntornoRSS import EntornoRSS
import logging
from alerts import process_alerts
from main import LOGGER_NOMBRE
from time import sleep

entorno = EntornoRSS()
db = Database()
logger = logging.getLogger(LOGGER_NOMBRE)

def fetch_de_entradas() -> None:
    fuentes = db.col_rss_fuentes.lista_fuentes()
    logger.info("Iniciando procesamiento de %d fuentes RSS", len(fuentes))

    total_nuevas = 0
    for fuente in fuentes:
        try:
            for entrada in fuente.obtener_entradas():
                if db.col_rss_entradas.insertar(entrada) is not None:
                    total_nuevas += 1
            
        except Exception:
            logger.exception("Error crítico en ingesta de fuente: %s", fuente.url)

    logger.info("Ciclo completado. Nuevas entradas detectadas: %d", total_nuevas)


def process_alerts_safely() -> int:
    """Ejecuta alertas sin tumbar el ciclo principal del worker."""
    try:
        return process_alerts(db)
    except Exception:
        logger.exception("Fallo el procesamiento de alertas")
        return 0

def fetch_entradas_task():
    fetch_de_entradas()

    # Las alertas se evaluan justo despues de ingerir nuevas entradas RSS.
    process_alerts_safely()

    while entorno.run_once == "false":
        sleep(entorno.intervalo_rss)
        try:
            fetch_de_entradas()
            # Fallos de alertas no deben impedir que el worker siga ingiriendo RSS.
            process_alerts_safely()
        except Exception:
            logger.exception("Fallo un ciclo completo de ingesta RSS")

__all__ = ["fetch_entradas_task"]
        
