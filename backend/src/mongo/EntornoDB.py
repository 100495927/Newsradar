from os import environ
from .constantes.entorno import *


class EntornoDB:
    def __init__(self):
        self.__root_usuario = environ.get(VARENV_MONGO_USUARIO_ROOT)
        if not self.__root_usuario:
            raise ValueError(
                f"Variable de entorno {VARENV_MONGO_USUARIO_ROOT} no encontrada"
            )
        self.__root_contraseña = environ.get(VARENV_MONGO_CONTRASEÑA_ROOT)
        if not self.__root_contraseña:
            raise ValueError(
                f"Variable de entorno {VARENV_MONGO_CONTRASEÑA_ROOT} no encontrada"
            )
        self.__app_usuario = environ.get(VARENV_USUARIO_MONGODB_APP)
        if not self.__app_usuario:
            raise ValueError(
                f"Variable de entorno {VARENV_USUARIO_MONGODB_APP} no encontrada"
            )
        self.__app_contraseña = environ.get(VARENV_CONTRASEÑA_MONGODB_APP)
        if not self.__app_contraseña:
            raise ValueError(
                f"Variable de entorno {VARENV_CONTRASEÑA_MONGODB_APP} no encontrada"
            )
        self.__puerto = environ.get(VARENV_PUERTO_LOCAL_MONGODB)
        if not self.__puerto:
            raise ValueError(
                f"Variable de entorno {VARENV_PUERTO_LOCAL_MONGODB} no encontrada"
            )
        self.__app_db_name = environ.get(VARENV_APP_DB_NAME)
        if not self.__app_db_name:
            raise ValueError(f"Variable de entorno {VARENV_APP_DB_NAME} no encontrada")
        self.__root_db_name = environ.get(VARENV_INITDB_DATABASE)
        if not self.__root_db_name:
            raise ValueError(
                f"Variable de entorno {VARENV_INITDB_DATABASE} no encontrada"
            )
        self.__host = environ.get(VARENV_MONGO_HOST)
        if not self.__host:
            raise ValueError(f"Variable de entorno {VARENV_MONGO_HOST} no encontrada")

    @property
    def root_usuario(self):
        if not self.__root_usuario:
            raise ValueError("Informacion de usuario de root no encontrada")
        return self.__root_usuario

    @property
    def root_contraseña(self):
        if not self.__root_contraseña:
            raise ValueError("Informacion de contraseña de root no encontrada")
        return self.__root_contraseña

    @property
    def app_usuario(self):
        if not self.__app_usuario:
            raise ValueError("Informacion de usuario de app no encontrada")
        return self.__app_usuario

    @property
    def app_contraseña(self):
        if not self.__app_contraseña:
            raise ValueError("Informacion de usuario de app no encontrada")
        return self.__app_contraseña

    @property
    def puerto(self):
        if not self.__puerto:
            raise ValueError("Puerto no encontrado")
        return self.__puerto

    @property
    def app_db_name(self):
        if not self.__app_db_name:
            raise ValueError("Nombre de db de app no encontrado")
        return self.__app_db_name

    @property
    def root_db_name(self):
        if not self.__root_db_name:
            raise ValueError("Nombre de db de root no encontrado")
        return self.__root_db_name

    @property
    def host(self):
        if not self.__host:
            raise ValueError("Host no encontrado")
        return self.__host


__all__ = ["EntornoDB"]
