from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unidecode import unidecode
from pymongo import UpdateOne

from .Coleccion import Coleccion

if TYPE_CHECKING:
    from rss.RSSEntrada import RSSEntrada

def _normalizar_raiz(texto: str) -> str:
    """
    Normalización simple: quita acentos, minúsculas y elimina las 2 últimas 
    letras de la última palabra para gestionar plurales y géneros.
    """
    if not texto or not isinstance(texto, str):
        return ""
    
    # 1. Quitar acentos y pasar a minúsculas
    limpio = unidecode(texto).lower().strip()
    
    # 2. Procesar la última palabra
    palabras = limpio.split()
    if not palabras:
        return ""
    
    ultima_palabra = palabras[-1]
    if len(ultima_palabra) > 2:
        palabras[-1] = ultima_palabra[:-2]
    else:
        palabras.pop() # Si es muy corta (1 o 2 letras), la eliminamos
        
    return " ".join(palabras).strip()

class ColeccionRssEntradas(Coleccion):
    NOMBRE_COLECCION = "rss_entradas"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": [
                "id_fuente",
                "titulo",
                "autores",
                "link",
                "fecha_publicacion",
                "hash_deduplicado",
                "fecha_ingestion",
            ],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "id_fuente": {"bsonType": "objectId"},
                "titulo": {"bsonType": "string"},
                "autores": {"bsonType": ["array", "null"]},
                "link": {"bsonType": "string"},
                "categorias": {"bsonType": ["array", "null"]},
                "categorias_raw": {"bsonType": ["array", "null"]},
                "resumen": {"bsonType": ["string", "null"]},
                "fecha_publicacion": {"bsonType": "date"},
                "hash_deduplicado": {"bsonType": "string"},
                "fecha_ingestion": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "hash_deduplicado", unique=True, name="idx_rss_entradas_hash_deduplicado_unique"
        )
        self._collection.create_index(
            [("id_fuente", 1), ("fecha_publicacion", -1)], name="idx_rss_entradas_fuente_fecha"
        )
        self._collection.create_index(
            [("fecha_publicacion", -1)], # Change to list with -1 to match init-mongo.js
            name="idx_rss_entradas_fecha_publicacion"
        )
        self._collection.create_index(
            "categorias", name="idx_rss_entradas_categorias"
        )

    def insertar(self, entrada: "RSSEntrada"):
        datos = entrada.a_mongo()
        url_fuente = entrada.fuente.url

        id_fuente = self._db_padre.col_rss_fuentes._collection.find_one({"url": url_fuente})
        if not id_fuente:
            raise ValueError(f"No se encontró la fuente en la BD para la URL: {url_fuente}")
        datos["id_fuente"] = id_fuente["_id"]
        datos.pop("fecha_ingestion")
        resultado = self._collection.update_one(
            {"hash_deduplicado": datos["hash_deduplicado"]},
            {
                "$setOnInsert": datos,
                "$set": {"fecha_ingestion": datetime.now(timezone.utc)},
            },
            upsert=True,
        )
        return resultado.upserted_id

    def migrar_categorias_nulas(self) -> None:
        """Sincroniza categorias_raw con IDs IPTC usando normalización simple."""
        mapa_raices = {}
        col_iptc = self._db_padre.col_rss_cat_iptc._collection
        
        # 1. Cargar mapa de raíces (proceso offline, sin descargas)
        for cat in col_iptc.find({}, {"_id": 1, "descripciones": 1}):
            for desc in cat.get('descripciones', []):
                # Generamos raíz para cada descripción (independiente del idioma)
                raiz = _normalizar_raiz(desc.get('nombre'))
                if raiz:
                    mapa_raices[raiz] = cat['_id']

        # 2. Buscar entradas pendientes
        query = {"categorias": {"$in": [None, []]}}
        entradas = self._collection.find(query, {"_id": 1, "categorias_raw": 1})

        operaciones = []
        for doc in entradas:
            ids_encontrados = set()
            raw_list = doc.get("categorias_raw") or []
            
            for raw in raw_list:
                raiz_raw = _normalizar_raiz(raw)
                if raiz_raw in mapa_raices:
                    ids_encontrados.add(mapa_raices[raiz_raw])

            # 3. Preparar Bulk Update
            operaciones.append(UpdateOne(
                {"_id": doc["_id"]},
                {
                    "$set": {
                        "categorias": list(ids_encontrados),
                        "fecha_ingestion": datetime.now(timezone.utc)
                    }
                }
            ))

        if operaciones:
            self._collection.bulk_write(operaciones, ordered=False)

__all__ = ["ColeccionRssEntradas"]