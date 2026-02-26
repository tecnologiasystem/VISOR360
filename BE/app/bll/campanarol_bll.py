# BLL para CampanasRolesQA
from app.dal.campanarol_dal import (
    crear_campanarol,
    obtener_campanasroles,
    actualizar_campanarol,
    eliminar_campanarol
)

class CampanaRolBLL:
    @staticmethod
    def crear(id_campana, id_rol):
        return crear_campanarol(id_campana, id_rol)

    @staticmethod
    def listar():
        return obtener_campanasroles()

    @staticmethod
    def actualizar(id_campanasrolesqa, id_campana, id_rol):
        return actualizar_campanarol(id_campanasrolesqa, id_campana, id_rol)

    @staticmethod
    def eliminar(id_campanasrolesqa):
        return eliminar_campanarol(id_campanasrolesqa)
