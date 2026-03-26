from pymongo import MongoClient
from abd import ABC, abstractmethod

class Coleccion():
    @abstractmethod
    def __init__(self, db: MongoClient):
        """Genera la coleccion"""

    @abstractmethod
    def esquema(self):
        """Retorna el esquema de validacion de la coleccion"""
        pass



__all__ = ["Coleccion"]