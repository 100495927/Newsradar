import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.insert(0, project_root)

from rss import generar_lista_estandar_feeds

if __name__ == "__main__":
    # Pruebas
    feeds = generar_lista_estandar_feeds()

    for feed in feeds.feeds:
        f = feed.obtener_entradas()
        print(f)
        for entrada in f.entradas[:1]:
            print(f"{entrada}\n\n")
