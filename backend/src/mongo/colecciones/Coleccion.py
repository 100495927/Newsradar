from abc import ABC, abstractmethod
import pymongo
from mongo.Database import Database


class Coleccion(ABC):
    NOMBRE_COLECCION: str | None = None

    def __init__(self, db_padre_objeto: Database):
        if not self.NOMBRE_COLECCION:
            raise ValueError("Debe definir NOMBRE_COLECCION en la subclase")

        self.__db_padre = db_padre_objeto
        self.__db_padre: Database = db_padre_objeto
        self._collection = self.__pym_db[self.NOMBRE_COLECCION]
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
        db = self.__db_padre.db
        if self.NOMBRE_COLECCION in db.list_collection_names():
            # Existe ya la coleccion (actualizar)
            db.command("collMod", self.NOMBRE_COLECCION, validator=validador)
        else:
            # No existe la collecion (crear)
            db.create_collection(self.NOMBRE_COLECCION, validator=validador)

    @property
    def __pym_db(self):
        return self.__db_padre.db
