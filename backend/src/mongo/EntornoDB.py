from dataclasses import dataclass
from os import environ
from .constantes.entorno import *


@dataclass
class EntornoDB:
    def __init__(self):
        self.__usuario = environ.get(VARENV_USUARIO_MONGODB_ROOT)
        if not self.__usuario:
            raise ValueError(f"Variable de entorno {VARENV_USUARIO_MONGODB_ROOT} no encontrada")
        self.__contraseña = environ.get(VARENV_CONTRASEÑA_MONGODB_ROOT)
        if not self.__contraseña:
            raise ValueError(ValueError(f"Variable de entorno {VARENV_CONTRASEÑA_MONGODB_ROOT} no encontrada"))
        self.__puerto_local = environ.get(VARENV_PUERTO_LOCAL_MONGODB)
        if not self.__puerto_local:
            raise ValueError(ValueError(f"Variable de entorno {VARENV_PUERTO_LOCAL_MONGODB} no encontrada"))
        self.__app_db_nombre = environ.get(VARENV_APP_DB)
        if not self.__app_db_nombre:
            raise ValueError(ValueError(f"Variable de entorno {VARENV_APP_DB} no encontrada"))



    @property
    def usuario(self):
        if not self.__usuario:
            raise ValueError("Informacion de usuario no encontrada")
        return self.__usuario

    @property
    def contraseña(self):
        if not self.__contraseña:
            raise ValueError("Informacion de contraseña no encontrada")
        return self.__contraseña

    @property
    def puerto_local(self):
        if not self.__puerto_local:
            raise ValueError("Puerto local no encontrado")
        return self.__puerto_local
        
    @property
    def app_db_nombre(self):
        if not self.__app_db_nombre:
            raise ValueError("Nombre de db no encontrado")
        return self.__app_db_nombre

__all__ = ["EntornoDB"]