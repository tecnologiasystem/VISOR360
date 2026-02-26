"""
BLL para Campañas
Lógica de negocio para campañas
"""
from typing import List, Optional
import logging
from dal import campana_dal
from models.campana import CampanaSimple, CampanaListResponse
from database import DatabaseError

logger = logging.getLogger(__name__)


class CampanaService:
    """Servicio de lógica de negocio para Campañas"""
    
    @staticmethod
    def obtener_todas_campanas() -> CampanaListResponse:
        """
        Obtiene todas las campañas para selectores del FE.
        
        Returns:
            CampanaListResponse con lista de campañas
        """
        try:
            campanas_raw = campana_dal.get_all_campanas()
            campanas = [
                CampanaSimple(
                    IDCampanasQA=c["IDCampanasQA"],
                    NombreCampana=c["NombreCampana"]
                ) for c in campanas_raw
            ]
            return CampanaListResponse(
                success=True,
                data=campanas,
                total=len(campanas)
            )
        except DatabaseError as e:
            logger.error(f"Error en servicio de campañas: {e}")
            raise
    
    @staticmethod
    def obtener_campana_por_id(id_campana: int) -> Optional[CampanaSimple]:
        """
        Obtiene una campaña por ID.
        
        Args:
            id_campana: ID de la campaña
        
        Returns:
            CampanaSimple o None
        """
        try:
            campana = campana_dal.get_campana_by_id(id_campana)
            if campana:
                return CampanaSimple(
                    IDCampanasQA=campana["IDCampanasQA"],
                    NombreCampana=campana["NombreCampana"]
                )
            return None
        except DatabaseError as e:
            logger.error(f"Error al obtener campaña {id_campana}: {e}")
            raise
    
    @staticmethod
    def obtener_campanas_con_inversionistas() -> List[dict]:
        """
        Obtiene campañas con sus inversionistas asociados.
        
        Returns:
            Lista estructurada de campañas con inversionistas
        """
        try:
            datos = campana_dal.get_campanas_con_inversionistas()
            
            # Agrupar por campaña
            campanas_dict = {}
            for row in datos:
                id_campana = row["IDCampanasQA"]
                if id_campana not in campanas_dict:
                    campanas_dict[id_campana] = {
                        "IDCampanasQA": id_campana,
                        "NombreCampana": row["NombreCampana"],
                        "inversionistas": []
                    }
                campanas_dict[id_campana]["inversionistas"].append({
                    "IDInversionistaQA": row["IDInversionistaQA"],
                    "NombreInversionistaQA": row["NombreInversionistaQA"],
                    "IDCampanasInversionistasQA": row["IDCampanasInversionistasQA"]
                })
            
            return list(campanas_dict.values())
        except DatabaseError as e:
            logger.error(f"Error al obtener campañas con inversionistas: {e}")
            raise
    
    @staticmethod
    def obtener_campanas_por_rol(id_rol: int) -> List[CampanaSimple]:
        """
        Obtiene campañas asociadas a un rol.
        
        Args:
            id_rol: ID del rol
        
        Returns:
            Lista de campañas del rol
        """
        try:
            campanas_raw = campana_dal.get_campanas_por_rol(id_rol)
            return [
                CampanaSimple(
                    IDCampanasQA=c["IDCampanasQA"],
                    NombreCampana=c["NombreCampana"]
                ) for c in campanas_raw
            ]
        except DatabaseError as e:
            logger.error(f"Error al obtener campañas por rol {id_rol}: {e}")
            raise
