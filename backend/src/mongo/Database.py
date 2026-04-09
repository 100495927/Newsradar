import pymongo
from mongo.EntornoDB import EntornoDB
from os import environ
from urllib.parse import quote_plus


class Database:
    def __init__(self):
        self.__entorno = EntornoDB()
        usuario_root = quote_plus(self.__entorno.root_usuario)
        contraseña_root = quote_plus(self.__entorno.root_contraseña)
        uri = (
            f"mongodb://{usuario_root}:{contraseña_root}"
            f"@{self.__entorno.host}:{self.__entorno.puerto}/{self.__entorno.root_db_name}"
            f"?authSource={self.__entorno.root_db_name}"
        )
        self.__cliente: pymongo.MongoClient = pymongo.MongoClient(uri)
        self.__db: pymongo.Database = self.__cliente[self.__entorno.app_db_name]
        self.iniciar_colecciones()
        self.relogin_en_app()

    def iniciar_colecciones(self):
        from . import colecciones

        self.col_rss_entradas = colecciones.ColeccionRssEntradas(self)
        self.col_rss_entradas_raw = colecciones.ColeccionRssEntradasRaw(self)
        self.col_rss_fuentes = colecciones.ColeccionRssFuentes(self)
        self.col_users = colecciones.ColeccionUsers(self)
        self.col_user_sesions = colecciones.ColeccionUserSessions(self)

    def relogin_en_app(self):
        """Se reloguea en la aplicacion con permisos de app"""
        usuario_app = quote_plus(self.__entorno.app_usuario)
        contraseña_app = quote_plus(self.__entorno.app_contraseña)
        uri = (
            f"mongodb://{usuario_app}:{contraseña_app}"
            f"@{self.__entorno.host}:{self.__entorno.puerto}/{self.__entorno.app_db_name}"
            f"?authSource={self.__entorno.app_db_name}"
        )
        self.__cliente: pymongo.MongoClient = pymongo.MongoClient(uri)
        self.__db: pymongo.Database = self.__cliente[self.__entorno.app_db_name]

    @property
    def cliente(self):
        return self.__cliente

    @property
    def db(self):
        return self.__db
