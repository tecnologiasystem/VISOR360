"""
BLL para Inversionistas
Lógica de negocio para inversionistas
"""
from typing import List, Optional
import logging
from dal import inversionista_dal
from models.inversionista import (
    InversionistaSimple, 
    InversionistaListResponse,
    CampanaInversionistaSimple
)
from database import DatabaseError

logger = logging.getLogger(__name__)


class InversionistaService:
    """Servicio de lógica de negocio para Inversionistas"""
    
    @staticmethod
    def obtener_todos_inversionistas(solo_activos: bool = True) -> InversionistaListResponse:
        """
        Obtiene todos los inversionistas para selectores del FE.
        
        Args:
            solo_activos: Si solo retorna activos
        
        Returns:
            InversionistaListResponse con lista de inversionistas
        """
        try:
            inversionistas_raw = inversionista_dal.get_all_inversionistas(solo_activos)
            inversionistas = [
                InversionistaSimple(
                    IDInversionistaQA=i["IDInversionistaQA"],
                    NombreInversionistaQA=i["NombreInversionistaQA"],
                    EsActivo=i.get("EsActivo", True)
                ) for i in inversionistas_raw
            ]
            return InversionistaListResponse(
                success=True,
                data=inversionistas,
                total=len(inversionistas)
            )
        except DatabaseError as e:
            logger.error(f"Error en servicio de inversionistas: {e}")
            raise
    
    @staticmethod
    def obtener_inversionista_por_id(id_inversionista: int) -> Optional[InversionistaSimple]:
        """
        Obtiene un inversionista por ID.
        
        Args:
            id_inversionista: ID del inversionista
        
        Returns:
            InversionistaSimple o None
        """
        try:
            inv = inversionista_dal.get_inversionista_by_id(id_inversionista)
            if inv:
                return InversionistaSimple(
                    IDInversionistaQA=inv["IDInversionistaQA"],
                    NombreInversionistaQA=inv["NombreInversionistaQA"],
                    EsActivo=inv.get("EsActivo", True)
                )
            return None
        except DatabaseError as e:
            logger.error(f"Error al obtener inversionista {id_inversionista}: {e}")
            raise
    
    @staticmethod
    def obtener_inversionistas_por_campana(
        id_campana: int, 
        solo_activos: bool = True
    ) -> List[InversionistaSimple]:
        """
        Obtiene los inversionistas de una campaña.
        
        Args:
            id_campana: ID de la campaña
            solo_activos: Si solo retorna activos
        
        Returns:
            Lista de inversionistas de la campaña
        """
        try:
            inversionistas_raw = inversionista_dal.get_inversionistas_por_campana(
                id_campana, solo_activos
            )
            return [
                InversionistaSimple(
                    IDInversionistaQA=i["IDInversionistaQA"],
                    NombreInversionistaQA=i["NombreInversionistaQA"],
                    EsActivo=True
                ) for i in inversionistas_raw
            ]
        except DatabaseError as e:
            logger.error(f"Error al obtener inversionistas de campaña {id_campana}: {e}")
            raise
    
    @staticmethod
    def obtener_todas_relaciones_campana_inversionista(
        solo_activos: bool = True
    ) -> List[CampanaInversionistaSimple]:
        """
        Obtiene todas las relaciones campaña-inversionista.
        
        Returns:
            Lista de relaciones
        """
        try:
            relaciones_raw = inversionista_dal.get_all_campanas_inversionistas(solo_activos)
            return [
                CampanaInversionistaSimple(
                    IDCampanasInversionistasQA=r["IDCampanasInversionistasQA"],
                    IDCampanasQA=r["IDCampanasQA"],
                    NombreCampana=r["NombreCampana"],
                    IDInversionistaQA=r["IDInversionistaQA"],
                    NombreInversionistaQA=r["NombreInversionistaQA"]
                ) for r in relaciones_raw
            ]
        except DatabaseError as e:
            logger.error(f"Error al obtener relaciones: {e}")
            raise
    
    @staticmethod
    def obtener_relacion_campana_inversionista(
        id_campana: int, 
        id_inversionista: int
    ) -> Optional[CampanaInversionistaSimple]:
        """
        Obtiene una relación específica campaña-inversionista.
        
        Args:
            id_campana: ID de la campaña
            id_inversionista: ID del inversionista
        
        Returns:
            CampanaInversionistaSimple o None
        """
        try:
            rel = inversionista_dal.get_campana_inversionista(id_campana, id_inversionista)
            if rel:
                return CampanaInversionistaSimple(
                    IDCampanasInversionistasQA=rel["IDCampanasInversionistasQA"],
                    IDCampanasQA=rel["IDCampanasQA"],
                    NombreCampana=rel["NombreCampana"],
                    IDInversionistaQA=rel["IDInversionistaQA"],
                    NombreInversionistaQA=rel["NombreInversionistaQA"]
                )
            return None
        except DatabaseError as e:
            logger.error(f"Error al obtener relación: {e}")
            raise
