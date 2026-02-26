"""
BLL para Recaudo
Lógica de negocio para recaudo diario y mensual
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
import logging
from dal import recaudo_dal
from models.recaudo import (
    ResumenRecaudoDia,
    ResumenRecaudoMes,
    RecaudoDiarioListResponse,
    RecaudoMensualListResponse,
    RecaudoDiarioExtendido
)
from models.common import FiltrosRecaudo
from database import DatabaseError

logger = logging.getLogger(__name__)


class RecaudoService:
    """Servicio de lógica de negocio para Recaudo"""
    
    # =========================================================================
    # CONSULTAS PARA DASHBOARD (usando SP_CampanasRecaudoQA_ConsultaFE)
    # =========================================================================
    
    @staticmethod
    def obtener_recaudo_diario(
        id_campana: Optional[int] = None,
        id_inversionista: Optional[int] = None,
        anio_mes: Optional[str] = None,
        anio_mes_desde: Optional[str] = None,
        anio_mes_hasta: Optional[str] = None,
        solo_activos: bool = True
    ) -> RecaudoDiarioListResponse:
        """
        Obtiene el resumen de recaudo diario para gráficos del FE.
        Usa SP_CampanasRecaudoQA_ConsultaFE con TipoResumen=1.
        
        Args:
            id_campana: Filtrar por campaña
            id_inversionista: Filtrar por inversionista
            anio_mes: Periodo específico YYYY-MM
            anio_mes_desde: Periodo inicio YYYY-MM
            anio_mes_hasta: Periodo fin YYYY-MM
            solo_activos: Solo registros activos
        
        Returns:
            RecaudoDiarioListResponse con datos para gráficos
        """
        try:
            datos = recaudo_dal.sp_consulta_fe_diario(
                id_campana=id_campana,
                id_inversionista=id_inversionista,
                anio_mes=anio_mes,
                anio_mes_desde=anio_mes_desde,
                anio_mes_hasta=anio_mes_hasta,
                solo_activos=solo_activos
            )
            
            resumenes = []
            for row in datos:
                resumenes.append(ResumenRecaudoDia(
                    IDCampanasQA=row.get("IDCampanasQA", 0),
                    NombreCampana=row.get("NombreCampana", ""),
                    IDInversionistaQA=row.get("IDInversionistaQA", 0),
                    NombreInversionistaQA=row.get("NombreInversionistaQA", ""),
                    AnioMes=row.get("AnioMes", ""),
                    DiaHabil=row.get("DiaHabil", 0),
                    ValorRecaudoDia=Decimal(str(row.get("ValorRecaudoDia", 0) or 0)),
                    MetaDia=Decimal(str(row.get("MetaDia", 0) or 0)),
                    DiferenciaDia=Decimal(str(row.get("DiferenciaDia", 0) or 0)),
                    PorcentajeCumplimientoDia=Decimal(str(row.get("PorcentajeCumplimientoDia", 0) or 0))
                ))
            
            return RecaudoDiarioListResponse(
                success=True,
                data=resumenes,
                total=len(resumenes),
                filters_applied={
                    "id_campana": id_campana,
                    "id_inversionista": id_inversionista,
                    "anio_mes": anio_mes,
                    "anio_mes_desde": anio_mes_desde,
                    "anio_mes_hasta": anio_mes_hasta
                }
            )
        except DatabaseError as e:
            logger.error(f"Error al obtener recaudo diario: {e}")
            raise
    
    @staticmethod
    def obtener_recaudo_mensual(
        id_campana: Optional[int] = None,
        id_inversionista: Optional[int] = None,
        anio_mes: Optional[str] = None,
        anio_mes_desde: Optional[str] = None,
        anio_mes_hasta: Optional[str] = None,
        solo_activos: bool = True
    ) -> RecaudoMensualListResponse:
        """
        Obtiene el resumen de recaudo mensual para gráficos del FE.
        Usa SP_CampanasRecaudoQA_ConsultaFE con TipoResumen=2.
        
        Args:
            id_campana: Filtrar por campaña
            id_inversionista: Filtrar por inversionista
            anio_mes: Periodo específico YYYY-MM
            anio_mes_desde: Periodo inicio YYYY-MM
            anio_mes_hasta: Periodo fin YYYY-MM
            solo_activos: Solo registros activos
        
        Returns:
            RecaudoMensualListResponse con datos para gráficos
        """
        try:
            datos = recaudo_dal.sp_consulta_fe_mensual(
                id_campana=id_campana,
                id_inversionista=id_inversionista,
                anio_mes=anio_mes,
                anio_mes_desde=anio_mes_desde,
                anio_mes_hasta=anio_mes_hasta,
                solo_activos=solo_activos
            )
            
            resumenes = []
            for row in datos:
                resumenes.append(ResumenRecaudoMes(
                    IDCampanasQA=row.get("IDCampanasQA", 0),
                    NombreCampana=row.get("NombreCampana", ""),
                    IDInversionistaQA=row.get("IDInversionistaQA", 0),
                    NombreInversionistaQA=row.get("NombreInversionistaQA", ""),
                    AnioMes=row.get("AnioMes", ""),
                    TotalRecaudoMes=Decimal(str(row.get("TotalRecaudoMes", 0) or 0)),
                    TotalMetaMes=Decimal(str(row.get("TotalMetaMes", 0) or 0)),
                    DiferenciaMes=Decimal(str(row.get("DiferenciaMes", 0) or 0)),
                    PorcentajeCumplimientoMes=Decimal(str(row.get("PorcentajeCumplimientoMes", 0) or 0))
                ))
            
            return RecaudoMensualListResponse(
                success=True,
                data=resumenes,
                total=len(resumenes),
                filters_applied={
                    "id_campana": id_campana,
                    "id_inversionista": id_inversionista,
                    "anio_mes": anio_mes,
                    "anio_mes_desde": anio_mes_desde,
                    "anio_mes_hasta": anio_mes_hasta
                }
            )
        except DatabaseError as e:
            logger.error(f"Error al obtener recaudo mensual: {e}")
            raise
    
    # =========================================================================
    # CONSULTAS DIRECTAS
    # =========================================================================
    
    @staticmethod
    def obtener_recaudo_por_id(id_recaudo: int) -> Optional[RecaudoDiarioExtendido]:
        """
        Obtiene un registro de recaudo por ID.
        
        Args:
            id_recaudo: ID del registro
        
        Returns:
            RecaudoDiarioExtendido o None
        """
        try:
            data = recaudo_dal.get_recaudo_by_id(id_recaudo)
            if data:
                return RecaudoDiarioExtendido(**data)
            return None
        except DatabaseError as e:
            logger.error(f"Error al obtener recaudo {id_recaudo}: {e}")
            raise
    
    @staticmethod
    def listar_recaudo(filtros: FiltrosRecaudo) -> List[dict]:
        """
        Lista registros de recaudo con filtros.
        
        Args:
            filtros: Filtros a aplicar
        
        Returns:
            Lista de registros
        """
        try:
            return recaudo_dal.listar_recaudo_diario(
                id_campana=filtros.IDCampanasQA,
                id_inversionista=filtros.IDInversionistaQA,
                anio_mes=filtros.AnioMes,
                anio_mes_desde=filtros.AnioMesDesde,
                anio_mes_hasta=filtros.AnioMesHasta,
                solo_activos=filtros.SoloActivos
            )
        except DatabaseError as e:
            logger.error(f"Error al listar recaudo: {e}")
            raise
    
    # =========================================================================
    # OPERACIONES CRUD VÍA SP
    # =========================================================================
    
    @staticmethod
    def crear_recaudo(
        id_campana_inversionista: int,
        anio_mes: str,
        dia_habil: int,
        valor_recaudo: Optional[Decimal],
        meta: Optional[Decimal],
        id_usuario: int,
        id_carga: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo registro de recaudo.
        
        Returns:
            Resultado de la operación
        """
        try:
            return recaudo_dal.sp_crud_recaudo(
                accion=1,  # INSERT
                id_campana_inversionista=id_campana_inversionista,
                anio_mes=anio_mes,
                dia_habil=dia_habil,
                valor_recaudo=valor_recaudo,
                meta=meta,
                id_usuario=id_usuario,
                id_carga=id_carga
            )
        except DatabaseError as e:
            logger.error(f"Error al crear recaudo: {e}")
            raise
    
    @staticmethod
    def actualizar_recaudo(
        id_recaudo: int,
        valor_recaudo: Optional[Decimal],
        meta: Optional[Decimal],
        id_usuario: int
    ) -> Dict[str, Any]:
        """
        Actualiza un registro de recaudo existente.
        
        Returns:
            Resultado de la operación
        """
        try:
            return recaudo_dal.sp_crud_recaudo(
                accion=2,  # UPDATE
                id_recaudo=id_recaudo,
                valor_recaudo=valor_recaudo,
                meta=meta,
                id_usuario=id_usuario
            )
        except DatabaseError as e:
            logger.error(f"Error al actualizar recaudo {id_recaudo}: {e}")
            raise
    
    @staticmethod
    def eliminar_recaudo(id_recaudo: int, id_usuario: int) -> Dict[str, Any]:
        """
        Elimina lógicamente un registro de recaudo.
        
        Returns:
            Resultado de la operación
        """
        try:
            return recaudo_dal.sp_crud_recaudo(
                accion=3,  # DELETE
                id_recaudo=id_recaudo,
                id_usuario=id_usuario
            )
        except DatabaseError as e:
            logger.error(f"Error al eliminar recaudo {id_recaudo}: {e}")
            raise
    
    # =========================================================================
    # RESÚMENES PARA DASHBOARD
    # =========================================================================
    
    @staticmethod
    def obtener_resumen_por_campana(
        anio_mes: str,
        id_campana: Optional[int] = None
    ) -> List[dict]:
        """
        Obtiene resumen de recaudo agrupado por campaña.
        
        Returns:
            Lista con totales por campaña
        """
        try:
            return recaudo_dal.get_resumen_recaudo_por_campana(anio_mes, id_campana)
        except DatabaseError as e:
            logger.error(f"Error al obtener resumen por campaña: {e}")
            raise
    
    @staticmethod
    def obtener_resumen_por_inversionista(
        anio_mes: str,
        id_campana: Optional[int] = None
    ) -> List[dict]:
        """
        Obtiene resumen de recaudo agrupado por inversionista.
        
        Returns:
            Lista con totales por inversionista
        """
        try:
            return recaudo_dal.get_resumen_recaudo_por_inversionista(anio_mes, id_campana)
        except DatabaseError as e:
            logger.error(f"Error al obtener resumen por inversionista: {e}")
            raise
    
    @staticmethod
    def obtener_acumulado_diario(
        anio_mes: str,
        id_campana: Optional[int] = None,
        id_inversionista: Optional[int] = None
    ) -> List[dict]:
        """
        Obtiene el acumulado diario de recaudo vs meta.
        Útil para gráficos de línea acumulada.
        
        Returns:
            Lista con acumulado por día hábil
        """
        try:
            return recaudo_dal.get_acumulado_diario(anio_mes, id_campana, id_inversionista)
        except DatabaseError as e:
            logger.error(f"Error al obtener acumulado diario: {e}")
            raise
