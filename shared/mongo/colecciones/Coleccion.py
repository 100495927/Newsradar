from __future__ import annotations

from abc import ABC
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

    @property
    def __pym_db_app(self):
        return self.__db_padre.db_app

    @property
    def _db_padre(self):
        return self.__db_padre
