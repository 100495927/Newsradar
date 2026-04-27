from __future__ import annotations

from typing import TYPE_CHECKING

from .Coleccion import Coleccion

if TYPE_CHECKING:
    from rss.iptc.IPTCCategoria import IPTCCategoria


class ColeccionRssCategoriasIPTC(Coleccion):
    NOMBRE_COLECCION = "rss_categorias_iptc"

    def esquema(self) -> dict:
        """Returns the MongoDB $jsonSchema validation."""
        return {
            "bsonType": "object",
            "required": ["_id", "descripciones"],
            "properties": {
                "_id": {"bsonType": "int"},
                "id_padre": {"bsonType": ["int", "null"]},
                "nivel": {"bsonType": ["int", "null"]},
                "descripciones": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "required": ["idioma", "nombre"],
                        "properties": {
                            "idioma": {"bsonType": "string"},
                            "nombre": {"bsonType": "string"},
                            "descripcion": {"bsonType": "string"},
                        },
                    },
                },
                "subcategorias": {
                    "bsonType": "array",
                    "items": {"bsonType": "int"},
                },
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "id_padre", 
            name="idx_rss_categorias_iptc_id_padre"
        )
        
        self._collection.create_index(
            [("descripciones.nombre", "text")], 
            name="idx_rss_categorias_iptc_nombre_text"
        )

    def insertar(self, categoria: "IPTCCategoria"):
        datos = categoria.a_mongo()
        self._collection.replace_one({"_id": datos["_id"]}, datos, upsert=True)

        for subcat in categoria.subcategorias:
            self.insertar(subcat)

    def insertar_json(self, lista_json: list[dict]):
        for doc in lista_json:
            self._collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)

    def id_por_nombre(self, nombre: str) -> int | None:
        query = {"descripciones.nombre": {"$regex": f"^{nombre}$", "$options": "i"}}
        
        resultado = self._collection.find_one(query, {"_id": 1})
        
        if resultado:
            return resultado["_id"]
        return None

__all__ = ["ColeccionRssCategoriasIPTC"]
 