#!/usr/bin/env python3
"""
Worker de ingesta RSS para ejecucion continua en contenedor dedicado.
Resultado esperado: en cada ciclo obtiene feeds RSS, persiste fuentes/entradas en MongoDB
(con deduplicacion por hash) y sincroniza a Elasticsearch.
"""

from __future__ import annotations

import os
import sys
import time
import traceback
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def run_cycle() -> tuple[int, int]:
    from mongo import Database  # pyright: ignore[reportMissingImports]
    from rss import generar_lista_estandar_feeds  # pyright: ignore[reportMissingImports]
    from rss_mongo_to_elasticsearch import sync as sync_mongo_to_es

    db = Database()
    feeds = generar_lista_estandar_feeds()

    fuentes_procesadas = 0
    entradas_procesadas = 0

    for feed in feeds.feeds:
        try:
            entradas = feed.obtener_entradas()
            db.col_rss_fuentes.insertar(feed)
            fuentes_procesadas += 1

            for entrada in entradas.entradas:
                db.col_rss_entradas.insertar(entrada)
                entradas_procesadas += 1
        except Exception:
            print(f"[rss-worker] Error procesando feed: {feed.url}")
            traceback.print_exc()

    try:
        sync_mongo_to_es()
    except Exception:
        print("[rss-worker] Error sincronizando Mongo -> Elasticsearch")
        traceback.print_exc()

    return fuentes_procesadas, entradas_procesadas


def main() -> None:
    intervalo = int(os.getenv("RSS_WORKER_INTERVAL_SECONDS", "300"))
    ejecutar_una_vez = _to_bool(os.getenv("RSS_WORKER_RUN_ONCE"), default=False)

    print(
        "[rss-worker] Iniciado. "
        f"intervalo={intervalo}s, run_once={ejecutar_una_vez}"
    )

    while True:
        inicio = time.time()
        try:
            fuentes, entradas = run_cycle()
            duracion = round(time.time() - inicio, 2)
            print(
                "[rss-worker] Ciclo completado: "
                f"fuentes={fuentes}, entradas={entradas}, duracion={duracion}s"
            )
        except Exception:
            print("[rss-worker] Error no controlado en ciclo")
            traceback.print_exc()

        if ejecutar_una_vez:
            print("[rss-worker] Finalizado en modo run_once")
            return

        time.sleep(intervalo)


if __name__ == "__main__":
    main()
