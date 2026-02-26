# BLL para CampanasQA
from app.dal.campana_dal import (
    crear_campana,
    obtener_campanas,
    actualizar_campana,
    eliminar_campana,
    obtener_campanas_por_usuario
)

class CampanaBLL:
    @staticmethod
    def crear(nombre, id_usuario_lider):
        return crear_campana(nombre, id_usuario_lider)

    @staticmethod
    def listar():
        return obtener_campanas()

    @staticmethod
    def actualizar(id_campana, nombre, id_usuario_lider):
        return actualizar_campana(id_campana, nombre, id_usuario_lider)

    @staticmethod
    def eliminar(id_campana):
        return eliminar_campana(id_campana)

    @staticmethod
    def listar_por_usuario(id_usuario):
        return obtener_campanas_por_usuario(id_usuario)
