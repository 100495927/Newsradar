from pymongo import MongoClient
from mongo.EntornoDB import EntornoDB
from os import environ


class Database:
    def __init__(self):
        self.__entorno = EntornoDB()
        uri = (
            f"mongodb://{self.__entorno.usuario}:{self.__entorno.contraseña}"
            f"@{self.__entorno.host}:{self.__entorno.puerto}/{self.__entorno.app_db_nombre}"
            f"?authSource={self.__entorno.app_db_nombre}"
        )
        self.__cliente: MongoClient = MongoClient(uri)
        self.__db: pymongo.Database = self.__cliente[self.__entorno.app_db_nombre]
        self.iniciar_colecciones()

    def iniciar_colecciones(self):
        from . import colecciones

        self.col_rss_entradas = colecciones.ColeccionRssEntradas(self.__db)
        self.col_rss_entradas_raw = colecciones.ColeccionRssEntradasRaw(self.__db)
        self.col_rss_fuentes = colecciones.ColeccionRssFuentes(self.__db)
        self.col_users = colecciones.ColeccionUsers(self.__db)
        self.col_user_sesions = colecciones.ColeccionUserSessions(self.__db)

    @property
    def cliente(self):
        return self.__cliente

    @property
    def db(self):
        return self.__db