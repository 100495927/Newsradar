import pymongo
from urllib.parse import quote_plus

from .EntornoDB import EntornoDB


class Database:
    def __init__(self):
        self.__entorno = EntornoDB()
        self.login_como_admin()
        self.login_como_app()

        self.iniciar_colecciones()

    def login_como_admin(self):
        usuario_root = quote_plus(self.__entorno.root_usuario)
        contraseña_root = quote_plus(self.__entorno.root_contraseña)
        uri = (
            f"mongodb://{usuario_root}:{contraseña_root}"
            f"@{self.__entorno.host}:{self.__entorno.puerto}/{self.__entorno.root_db_name}"
            f"?authSource={self.__entorno.root_db_name}"
        )
        self.__cliente_admin: pymongo.MongoClient = pymongo.MongoClient(uri)
        self.__db__admin: pymongo.Database = self.__cliente_admin[self.__entorno.app_db_name]

    def login_como_app(self):
        usuario_app = quote_plus(self.__entorno.app_usuario)
        contraseña_app = quote_plus(self.__entorno.app_contraseña)
        uri = (
            f"mongodb://{usuario_app}:{contraseña_app}"
            f"@{self.__entorno.host}:{self.__entorno.puerto}/{self.__entorno.app_db_name}"
            f"?authSource={self.__entorno.app_db_name}"
        )
        self.__cliente_app: pymongo.MongoClient = pymongo.MongoClient(uri)
        self.__db_app: pymongo.Database = self.__cliente_app[self.__entorno.app_db_name]

    def iniciar_colecciones(self):
        from . import colecciones

        self.col_rss_entradas = colecciones.ColeccionRssEntradas(self)
        self.col_rss_fuentes = colecciones.ColeccionRssFuentes(self)
        self.col_users = colecciones.ColeccionUsers(self)
        self.col_user_sesions = colecciones.ColeccionUserSessions(self)

    def ping(self) -> None:
        self.__cliente_app.admin.command("ping")

    @property
    def cliente_admin(self):
        return self.__cliente_admin

    @property
    def db_admin(self):
        return self.__db__admin

    @property
    def db_app(self):
        return self.__db_app

