from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Database import Database


class Coleccion(ABC):
    NOMBRE_COLECCION: str | None = None

    def __init__(self, db_padre_objeto: Database):
        if not self.NOMBRE_COLECCION:
            raise ValueError("Debe definir NOMBRE_COLECCION en la subclase")

        self.__db_padre = db_padre_objeto
        self.__db_padre: Database = db_padre_objeto
        self._collection = self.__pym_db_app[self.NOMBRE_COLECCION]

    @abstractmethod
    def esquema(self) -> dict:
        """Define el esquema/validador de la coleccion."""
        pass

    @abstractmethod
    def crear_indices(self):
        """Define e integra los índices de la colección"""
        pass

    def verificar_existencia(self) -> None:
        """Comprueba que la colección ya existe en MongoDB."""
        if self.NOMBRE_COLECCION not in self.__pym_db_app.list_collection_names():
            raise RuntimeError(f"La coleccion {self.NOMBRE_COLECCION} no existe en MongoDB")

    @property
    def __pym_db_admin(self):
        return self.__db_padre.db_admin

    @property
    def __pym_db_app(self):
        return self.__db_padre.db_app

    @property
    def _db_padre(self):
        return self.__db_padre

__all__ = ["Coleccion"]