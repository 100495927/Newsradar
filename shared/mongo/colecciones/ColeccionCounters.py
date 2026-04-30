from __future__ import annotations

from .Coleccion import Coleccion

class ColeccionCounters(Coleccion):
    """
    Gestión de la colección 'counters' en MongoDB.
    Esta colección se utiliza para generar IDs numéricos incrementales 
    para otras entidades del sistema como alertas o notificaciones.
    """
    NOMBRE_COLECCION = "counters"

    def __init__(self, db_padre_objeto: Database):
        super().__init__(db_padre_objeto)
        self.asegurar_contadores_iniciales()

    def esquema(self):
        """
        Retorna el esquema de validación JSON para los contadores.
        Asegura que cada secuencia tenga un ID de string, un valor secuencial
        numérico y una fecha de actualización.
        """
        return {
            "bsonType": "object",
            "required": ["_id", "seq", "updated_at"],
            "properties": {
                "_id": {
                    "bsonType": "string",
                    "description": "Nombre del contador (ej. 'alerts', 'notifications')"
                },
                "seq": {
                    "bsonType": ["int", "long"],
                    "description": "Valor actual de la secuencia"
                },
                "updated_at": {
                    "bsonType": "date",
                    "description": "Fecha de la última actualización del contador"
                },
            },
        }

    def crear_indices(self):
        """
        Crea los índices para la colección counters.
        En este caso, la colección utiliza el campo '_id' como clave primaria,
        por lo que no requiere índices adicionales según la definición original.
        """
        pass

    def asegurar_contadores_iniciales(self):
        """
        Inicializa los contadores requeridos por el sistema si no existen.
        """
        contadores = [
            "information_sources",
            "rss_channels",
            "alerts",
            "notifications"
        ]
        
        from datetime import datetime
        
        for nombre in contadores:
            self._collection.update_one(
                {"_id": nombre},
                {
                    "$setOnInsert": {
                        "_id": nombre,
                        "seq": 0,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )

__all__ = ["ColeccionCounters"]