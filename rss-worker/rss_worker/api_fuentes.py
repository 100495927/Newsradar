from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from rss import RSSFuente
from shared.mongo import Database
from EntornoRSS import EntornoRSS

app = FastAPI()
entorno = EntornoRSS()
db: Database | None = None


def get_db() -> Database:
    global db
    if db is None:
        db = Database()
    return db


class FuenteJSON(BaseModel):
    medio: str
    rss: str
    url: str
    activo: bool
    categoria_iptc: Optional[str] = None


@app.post("/fuentes")
async def actualizar_fuente(fuente: FuenteJSON):
    db = get_db()
    try:
        if fuente.categoria_iptc:
            cat = db.col_rss_cat_iptc.id_por_nombre(fuente.categoria_iptc)
        else:
            cat = None
        objecto_fuente = RSSFuente(
            fuente.medio,
            fuente.rss,
            fuente.url,
            fuente.activo,
            categoria_iptc=cat,
        )
        db.col_rss_fuentes.insertar(objecto_fuente)

        return {"message": "Fuente insertada"}
    except Exception as e:
        return {"message": str(e)}



def api_task():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=entorno.puerto_uvicorn)


__all__ = ["api_task"]
