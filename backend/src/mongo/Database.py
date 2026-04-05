from pymongo import MongoClient
from mongo.EntornoDB import EntornoDB
from os import environ


class Database:
    def __init__(self):
        self.__entorno = EntornoDB()
        uri = environ.get("MONGODB_URI")
        if not uri:
            uri = (
                f"mongodb://{self.__entorno.usuario}:{self.__entorno.contraseña}"
                f"@localhost:{self.__entorno.puerto_local}/{self.__entorno.app_db_nombre}?authSource=admin"
            )
        self.__cliente: MongoClient = MongoClient(
            uri
        )
        self.__db = self.__cliente[self.__entorno.app_db_nombre]
        self.iniciar_colecciones()

    def iniciar_colecciones(self):
        from . import colecciones

        self.col_rss_entradas = colecciones.ColeccionRssEntradas(self.__db)
        self.col_rss_entradas_raw = colecciones.ColeccionRssEntradasRaw(self.__db)
        self.col_rss_fuentes = colecciones.ColeccionRssFuentes(self.__db)
        self.col_users = colecciones.ColeccionUsers(self.__db)
        self.col_user_sesions = colecciones.ColeccionUserSessions(self.__db)
