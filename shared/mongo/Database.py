from collections.abc import Iterable
import pymongo
from urllib.parse import quote_plus

from .EntornoDB import EntornoDB


class Database:
    def __init__(self, required_collection_names: Iterable[str] | None = None):
        self.__entorno = EntornoDB()
        self.login_como_admin()
        self.login_como_app()

        self.iniciar_colecciones()
        if required_collection_names is None:
            self.verificar_colecciones()
        else:
            self.verificar_colecciones_requeridas(required_collection_names)

    def login_como_admin(self):
        usuario_root = quote_plus(self.__entorno.root_usuario)
        contraseña_root = quote_plus(self.__entorno.root_contraseña)
        uri = (
            f"mongodb://{usuario_root}:{contraseña_root}"
            f"@{self.__entorno.host}:{self.__entorno.puerto}/{self.__entorno.root_db_name}"
            f"?authSource={self.__entorno.root_db_name}"
        )
        self.__cliente_admin: pymongo.MongoClient = pymongo.MongoClient(uri)
        self.__db__admin: pymongo.Database = self.__cliente_admin[
            self.__entorno.app_db_name
        ]

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
        self.col_rss_cat_iptc = colecciones.ColeccionRssCategoriasIPTC(self)
        self.col_users = colecciones.ColeccionUsers(self)
        self.col_user_sesions = colecciones.ColeccionUserSessions(self)
        self.col_alertas = colecciones.ColeccionAlerts(self)
        self.col_counters = colecciones.ColeccionCounters(self)
        self.col_notifications = colecciones.ColeccionNotifications(self)

    def verificar_colecciones(self):
        faltantes = self._missing_collection_names(
            (
                self.col_rss_entradas.NOMBRE_COLECCION,
                self.col_rss_fuentes.NOMBRE_COLECCION,
                self.col_rss_cat_iptc.NOMBRE_COLECCION,
                self.col_user_sesions.NOMBRE_COLECCION,
                self.col_users.NOMBRE_COLECCION,
                self.col_alertas.NOMBRE_COLECCION,
                self.col_counters.NOMBRE_COLECCION,
                self.col_notifications.NOMBRE_COLECCION,
            )
        )
        if faltantes:
            raise RuntimeError(
                "Faltan colecciones requeridas en MongoDB: " + ", ".join(sorted(faltantes))
            )

    def verificar_colecciones_requeridas(
        self, required_collection_names: Iterable[str]
    ) -> None:
        faltantes = self._missing_collection_names(required_collection_names)
        if faltantes:
            raise RuntimeError(
                "Faltan colecciones requeridas en MongoDB: " + ", ".join(sorted(faltantes))
            )

    def _missing_collection_names(
        self, required_collection_names: Iterable[str]
    ) -> list[str]:
        colecciones_existentes = set(self.__db_app.list_collection_names())
        return [
            nombre
            for nombre in required_collection_names
            if nombre not in colecciones_existentes
        ]

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
