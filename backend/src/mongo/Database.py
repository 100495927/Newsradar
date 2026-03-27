from pymongo import MongoClient
from mongo.EntornoDB import EntornoDB


class Database:
    def __init__(self):
        self.__entorno = EntornoDB()
        self.__cliente: MongoClient = MongoClient(
            f"mongodb://localhost:{27017}/"
        )
        self.__db = self.__cliente[self.__entorno.app_db_nombre]
        self.crear_usuario_admin()
        self.iniciar_colecciones()

    def crear_usuario_admin(self):
        db = self.__db
        existe_admin = db.command("usersInfo", self.__entorno.usuario)

        if not existe_admin:
            db.command(
                "createUser",
                self.__entorno.usuario,
                pwd=self.__entorno.contraseña,
                roles=["readWrite"],
            )

    def iniciar_colecciones(self):
        import colecciones

        self.col_rss_entradas = colecciones.ColeccionRssEntradas(self.__db)
        self.col_rss_fuentes = colecciones.ColeccionRssFuentes(self.__db)
        self.col_users = colecciones.ColeccionUsers(self.__db)
        self.col_user_sesions = colecciones.ColeccionUserSessions(self.__db)
