from datetime import datetime, timezone

from .Coleccion import Coleccion


class ColeccionRssEntradasRaw(Coleccion):
    NOMBRE_COLECCION = "rss_entradas_raw"

    def esquema(self):
        return {
            "bsonType": "object",
            "required": ["id_entrada", "id_fuente", "payload_raw", "fecha_captura"],
            "properties": {
                "_id": {"bsonType": "objectId"},
                "id_entrada": {"bsonType": "objectId"},
                "id_fuente": {"bsonType": "objectId"},
                "payload_raw": {"bsonType": "string"},
                "formato_payload": {"bsonType": ["string", "null"]},
                "fecha_captura": {"bsonType": "date"},
            },
        }

    def crear_indices(self):
        self._collection.create_index(
            "id_entrada", unique=True, name="idx_rss_entradas_raw_id_entrada_unique"
        )
        self._collection.create_index(
            [("id_fuente", 1), ("fecha_captura", -1)],
            name="idx_rss_entradas_raw_fuente_fecha",
        )

    def insertar(self, id_entrada, id_fuente, payload_raw: str, formato_payload: str | None = None):
        return self._collection.insert_one(
            {
                "id_entrada": id_entrada,
                "id_fuente": id_fuente,
                "payload_raw": payload_raw,
                "formato_payload": formato_payload,
                "fecha_captura": datetime.now(timezone.utc),
            }
        )
