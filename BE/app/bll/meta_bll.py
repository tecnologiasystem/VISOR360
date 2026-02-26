# BLL para Metas
from app.dal.meta_dal import (
    obtener_metas_por_pais_mes,
    obtener_meta_general_pais,
    crear_meta,
    actualizar_meta,
    eliminar_meta,
    obtener_paises
)

class MetaBLL:
    
    @staticmethod
    def obtener_metas_mes(id_pais: int, mes: int, anio: int):
        """
        Obtiene todas las metas de un país para un mes específico
        """
        return obtener_metas_por_pais_mes(id_pais, mes, anio)
    
    @staticmethod
    def obtener_meta_pais(id_pais: int, mes: int, anio: int):
        """
        Obtiene solo la meta general del país (campaña grande)
        """
        return obtener_meta_general_pais(id_pais, mes, anio)
    
    @staticmethod
    def crear_nueva_meta(id_pais: int, mes: int, anio: int, monto_meta: float,
                         id_campana: int = None, usuario_creacion: int = None):
        """
        Crea una meta nueva con validaciones
        """
        if monto_meta <= 0:
            raise ValueError("El monto de la meta debe ser mayor a cero")
        
        if mes < 1 or mes > 12:
            raise ValueError("Mes debe estar entre 1 y 12")
        
        if anio < 2020:
            raise ValueError("Año inválido")
        
        return crear_meta(id_pais, mes, anio, monto_meta, id_campana, usuario_creacion)
    
    @staticmethod
    def modificar_meta(id_meta: int, monto_meta: float):
        """
        Actualiza una meta existente
        """
        if monto_meta <= 0:
            raise ValueError("El monto de la meta debe ser mayor a cero")
        
        return actualizar_meta(id_meta, monto_meta)
    
    @staticmethod
    def borrar_meta(id_meta: int):
        """
        Elimina una meta
        """
        return eliminar_meta(id_meta)
    
    @staticmethod
    def listar_paises():
        """
        Lista todos los países (campañas grandes)
        """
        return obtener_paises()
