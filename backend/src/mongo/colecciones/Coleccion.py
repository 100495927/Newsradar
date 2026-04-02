from abc import ABC, abstractmethod
from pymongo.database import Database

class Coleccion(ABC):
    NOMBRE_COLECCION: str | None = None

    def __init__(self, db: Database):
        if not self.NOMBRE_COLECCION:
            raise ValueError("Debe definir NOMBRE_COLECCION en la subclase")
            
        self._db = db
        self._collection = self._db[self.NOMBRE_COLECCION]
        self._inicializar_esquema()
        self.crear_indices()

    @abstractmethod
    def esquema(self):
        """Define el esquema/validador de la coleccion."""
        pass

    @abstractmethod
    def crear_indices(self):
        """Define e integra los índices de la colección"""
        pass
    
    def generar_indices(self):
        pass

    def _inicializar_esquema(self):
        """Aplica o crea la colección con el validador definido."""
        validador = {"$jsonSchema": self.esquema()}

        if self.NOMBRE_COLECCION in self._db.list_collection_names():
            # Existe ya la coleccion (actualizar)
            self._db.command("collMod", self.NOMBRE_COLECCION, validator=validador)
        else:
            # No existe la collecion (crear)
            self._db.create_collection(self.NOMBRE_COLECCION, validator=validador)