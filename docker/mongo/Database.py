from pymongo import MongoClient
from .EntornoDB import EntornoDB


class Database:
    def __init__(self):
        self.__entorno = EntornoDB()
        self.__cliente = MongoClient(f"mongodb://localhost:{entorno.puerto_local}/")
        self.crear_usuario_admin()

    def crear_usuario_admin(self):
        existe_admin = db.command("usersInfo", self.__entorno.usuario)
        if not existe_admin:
            db.command(
                "createUser",
                self.__entorno.usuario,
                pwd=self.__entorno.contraseña,
                roles=["readWrite"],
            )
