import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from pathlib import Path

c = Path(__file__).resolve().parent.parent.parent
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env.example"
load_dotenv(dotenv_path)

def main():
    from rss import generar_lista_estandar_feeds
    from mongo import Database
    
    db = Database()
    feeds = generar_lista_estandar_feeds()
    for feed in feeds.feeds:
        entradas = feed.obtener_entradas()
        db.col_rss_fuentes.insertar(feed)
        for entrada in entradas.entradas:
            db.col_rss_entradas.insertar(entrada)


if __name__ == "__main__":
    main()