from os import environ
from .constantes.entorno import *


class EntornoDB:
    @staticmethod
    def _get_env(*names: str) -> str | None:
        for name in names:
            value = environ.get(name)
            if value:
                return value
        return None

    def __init__(self, require_root: bool = False):
        self.__root_usuario = self._get_env(VARENV_MONGO_USUARIO_ROOT)
        self.__root_contraseña = self._get_env(VARENV_MONGO_CONTRASEÑA_ROOT)
        self.__root_db_name = self._get_env(VARENV_INITDB_DATABASE)
        self.__host = self._get_env(VARENV_MONGO_HOST)
        self.__puerto = self._get_env(VARENV_PUERTO_MONGODB)
        self.__app_usuario = self._get_env(VARENV_USUARIO_MONGODB_APP)
        if not self.__app_usuario:
            raise ValueError(
                f"Variable de entorno {VARENV_USUARIO_MONGODB_APP} no encontrada"
            )
        self.__app_contraseña = self._get_env(VARENV_CONTRASEÑA_MONGODB_APP)
        if not self.__app_contraseña:
            raise ValueError(
                f"Variable de entorno {VARENV_CONTRASEÑA_MONGODB_APP} no encontrada"
            )
        if not self.__puerto:
            raise ValueError(f"Variable de entorno {VARENV_PUERTO_MONGODB} no encontrada")
        self.__app_db_name = self._get_env(VARENV_APP_DB_NAME)
        if not self.__app_db_name:
            raise ValueError(f"Variable de entorno {VARENV_APP_DB_NAME} no encontrada")
        if not self.__host:
            raise ValueError(f"Variable de entorno {VARENV_MONGO_HOST} no encontrada")
        if require_root:
            if not self.__root_usuario:
                raise ValueError(
                    f"Variable de entorno {VARENV_MONGO_USUARIO_ROOT} no encontrada"
                )
            if not self.__root_contraseña:
                raise ValueError(
                    f"Variable de entorno {VARENV_MONGO_CONTRASEÑA_ROOT} no encontrada"
                )
            if not self.__root_db_name:
                raise ValueError(
                    f"Variable de entorno {VARENV_INITDB_DATABASE} no encontrada"
                )

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
