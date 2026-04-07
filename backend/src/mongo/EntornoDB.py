from os import environ
from .constantes.entorno import *


class EntornoDB:
    def __init__(self):
        self.__usuario = environ.get(VARENV_USUARIO_MONGODB_APP)
        if not self.__usuario:
            raise ValueError(f"Variable de entorno {VARENV_USUARIO_MONGODB_APP} no encontrada")
        self.__contraseña = environ.get(VARENV_CONTRASEÑA_MONGODB_APP)
        if not self.__contraseña:
            raise ValueError(f"Variable de entorno {VARENV_CONTRASEÑA_MONGODB_APP} no encontrada")
        self.__puerto = environ.get(VARENV_PUERTO_LOCAL_MONGODB)
        if not self.__puerto:
            raise ValueError(f"Variable de entorno {VARENV_PUERTO_LOCAL_MONGODB} no encontrada")
        self.__app_db_nombre = environ.get(VARENV_APP_DB)
        if not self.__app_db_nombre:
            raise ValueError(f"Variable de entorno {VARENV_APP_DB} no encontrada")
        self.__host = environ.get(VARENV_MONGO_HOST)
        if not self.__host:
            raise ValueError(f"Variable de entorno {VARENV_MONGO_HOST} no encontrada")


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
    def puerto(self):
        if not self.__puerto:
            raise ValueError("Puerto no encontrado")
        return self.__puerto
        
    @property
    def app_db_nombre(self):
        if not self.__app_db_nombre:
            raise ValueError("Nombre de db no encontrado")
        return self.__app_db_nombre

    @property
    def host(self):
        if not self.__host:
            raise ValueError("Host no encontrado")
        return self.__host

__all__ = ["EntornoDB"]