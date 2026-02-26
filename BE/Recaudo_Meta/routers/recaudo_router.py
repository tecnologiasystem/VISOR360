"""
Router para Recaudo
Endpoints: /recaudo
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List
from decimal import Decimal
import logging

from bll.recaudo_bll import RecaudoService
from bll.carga_bll import CargaRecaudoService
from models.recaudo import (
    RecaudoDiarioListResponse,
    RecaudoMensualListResponse,
    RecaudoDiarioCreate,
    RecaudoDiarioUpdate
)
from models.carga import CargaDesdeExcelRequest, CargaRecaudoResponse
from models.common import ErrorResponse, FiltrosRecaudo, APIResponse
from database import DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recaudo",
    tags=["Recaudo"],
    responses={
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)


# =============================================================================
# ENDPOINTS PARA DASHBOARD (usando SP_CampanasRecaudoQA_ConsultaFE)
# =============================================================================

@router.get(
    "/diario",
    response_model=RecaudoDiarioListResponse,
    summary="Obtener recaudo diario",
    description="Obtiene el resumen de recaudo diario para gráficos. Usa SP_CampanasRecaudoQA_ConsultaFE con TipoResumen=1"
)
async def obtener_recaudo_diario(
    id_campana: Optional[int] = Query(None, description="Filtrar por ID de campaña"),
    id_inversionista: Optional[int] = Query(None, description="Filtrar por ID de inversionista"),
    anio_mes: Optional[str] = Query(None, description="Periodo específico YYYY-MM"),
    anio_mes_desde: Optional[str] = Query(None, description="Periodo desde YYYY-MM"),
    anio_mes_hasta: Optional[str] = Query(None, description="Periodo hasta YYYY-MM"),
    solo_activos: bool = Query(True, description="Solo registros activos")
):
    """
    Obtiene el resumen de recaudo diario para gráficos del FE.
    
    Devuelve: IDCampanasQA, NombreCampana, IDInversionistaQA, NombreInversionistaQA,
    AnioMes, DiaHabil, ValorRecaudoDia, MetaDia, DiferenciaDia, PorcentajeCumplimientoDia
    """
    try:
        return RecaudoService.obtener_recaudo_diario(
            id_campana=id_campana,
            id_inversionista=id_inversionista,
            anio_mes=anio_mes,
            anio_mes_desde=anio_mes_desde,
            anio_mes_hasta=anio_mes_hasta,
            solo_activos=solo_activos
        )
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo diario: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener recaudo diario: {str(e)}"
        )


@router.get(
    "/mensual",
    response_model=RecaudoMensualListResponse,
    summary="Obtener recaudo mensual",
    description="Obtiene el resumen de recaudo mensual para gráficos. Usa SP_CampanasRecaudoQA_ConsultaFE con TipoResumen=2"
)
async def obtener_recaudo_mensual(
    id_campana: Optional[int] = Query(None, description="Filtrar por ID de campaña"),
    id_inversionista: Optional[int] = Query(None, description="Filtrar por ID de inversionista"),
    anio_mes: Optional[str] = Query(None, description="Periodo específico YYYY-MM"),
    anio_mes_desde: Optional[str] = Query(None, description="Periodo desde YYYY-MM"),
    anio_mes_hasta: Optional[str] = Query(None, description="Periodo hasta YYYY-MM"),
    solo_activos: bool = Query(True, description="Solo registros activos")
):
    """
    Obtiene el resumen de recaudo mensual para gráficos del FE.
    
    Devuelve: IDCampanasQA, NombreCampana, IDInversionistaQA, NombreInversionistaQA,
    AnioMes, TotalRecaudoMes, TotalMetaMes, DiferenciaMes, PorcentajeCumplimientoMes
    """
    try:
        return RecaudoService.obtener_recaudo_mensual(
            id_campana=id_campana,
            id_inversionista=id_inversionista,
            anio_mes=anio_mes,
            anio_mes_desde=anio_mes_desde,
            anio_mes_hasta=anio_mes_hasta,
            solo_activos=solo_activos
        )
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo mensual: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener recaudo mensual: {str(e)}"
        )


# =============================================================================
# ENDPOINTS DE RESÚMENES ADICIONALES
# =============================================================================

@router.get(
    "/resumen/por-campana",
    summary="Resumen de recaudo por campaña",
    description="Obtiene totales de recaudo agrupados por campaña para un mes"
)
async def resumen_por_campana(
    anio_mes: str = Query(..., description="Periodo YYYY-MM"),
    id_campana: Optional[int] = Query(None, description="Filtrar por campaña específica")
):
    """
    Obtiene resumen de recaudo agrupado por campaña.
    """
    try:
        datos = RecaudoService.obtener_resumen_por_campana(anio_mes, id_campana)
        return {
            "success": True,
            "data": datos,
            "total": len(datos),
            "anio_mes": anio_mes
        }
    except DatabaseError as e:
        logger.error(f"Error al obtener resumen por campaña: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener resumen: {str(e)}"
        )


@router.get(
    "/resumen/por-inversionista",
    summary="Resumen de recaudo por inversionista",
    description="Obtiene totales de recaudo agrupados por inversionista para un mes"
)
async def resumen_por_inversionista(
    anio_mes: str = Query(..., description="Periodo YYYY-MM"),
    id_campana: Optional[int] = Query(None, description="Filtrar por campaña")
):
    """
    Obtiene resumen de recaudo agrupado por inversionista.
    """
    try:
        datos = RecaudoService.obtener_resumen_por_inversionista(anio_mes, id_campana)
        return {
            "success": True,
            "data": datos,
            "total": len(datos),
            "anio_mes": anio_mes
        }
    except DatabaseError as e:
        logger.error(f"Error al obtener resumen por inversionista: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener resumen: {str(e)}"
        )


@router.get(
    "/acumulado-diario",
    summary="Acumulado diario de recaudo",
    description="Obtiene el acumulado diario de recaudo vs meta para gráficos de línea"
)
async def acumulado_diario(
    anio_mes: str = Query(..., description="Periodo YYYY-MM"),
    id_campana: Optional[int] = Query(None, description="Filtrar por campaña"),
    id_inversionista: Optional[int] = Query(None, description="Filtrar por inversionista")
):
    """
    Obtiene el acumulado diario de recaudo vs meta.
    Útil para gráficos de línea acumulada.
    """
    try:
        datos = RecaudoService.obtener_acumulado_diario(
            anio_mes, id_campana, id_inversionista
        )
        return {
            "success": True,
            "data": datos,
            "total": len(datos),
            "anio_mes": anio_mes
        }
    except DatabaseError as e:
        logger.error(f"Error al obtener acumulado diario: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener acumulado: {str(e)}"
        )


# =============================================================================
# ENDPOINTS CRUD
# =============================================================================

@router.get(
    "/{id_recaudo}",
    summary="Obtener registro de recaudo por ID",
    description="Obtiene un registro específico de recaudo con todos sus datos"
)
async def obtener_recaudo(id_recaudo: int):
    """
    Obtiene un registro de recaudo por ID.
    """
    try:
        recaudo = RecaudoService.obtener_recaudo_por_id(id_recaudo)
        if not recaudo:
            raise HTTPException(
                status_code=404,
                detail=f"Registro de recaudo con ID {id_recaudo} no encontrado"
            )
        return {
            "success": True,
            "data": recaudo.model_dump()
        }
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo {id_recaudo}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener recaudo: {str(e)}"
        )


@router.post(
    "/",
    summary="Crear registro de recaudo",
    description="Crea un nuevo registro de recaudo diario"
)
async def crear_recaudo(
    id_campana_inversionista: int = Body(..., description="ID de relación campaña-inversionista"),
    anio_mes: str = Body(..., description="Periodo YYYY-MM"),
    dia_habil: int = Body(..., ge=1, le=31, description="Día hábil"),
    valor_recaudo: Optional[float] = Body(None, description="Valor de recaudo"),
    meta: Optional[float] = Body(None, description="Meta"),
    id_usuario: int = Body(..., description="ID del usuario que crea")
):
    """
    Crea un nuevo registro de recaudo.
    """
    try:
        resultado = RecaudoService.crear_recaudo(
            id_campana_inversionista=id_campana_inversionista,
            anio_mes=anio_mes,
            dia_habil=dia_habil,
            valor_recaudo=Decimal(str(valor_recaudo)) if valor_recaudo else None,
            meta=Decimal(str(meta)) if meta else None,
            id_usuario=id_usuario
        )
        return {
            "success": True,
            "data": resultado,
            "message": "Registro creado exitosamente"
        }
    except DatabaseError as e:
        logger.error(f"Error al crear recaudo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear recaudo: {str(e)}"
        )


@router.put(
    "/{id_recaudo}",
    summary="Actualizar registro de recaudo",
    description="Actualiza un registro de recaudo existente"
)
async def actualizar_recaudo(
    id_recaudo: int,
    valor_recaudo: Optional[float] = Body(None, description="Nuevo valor de recaudo"),
    meta: Optional[float] = Body(None, description="Nueva meta"),
    id_usuario: int = Body(..., description="ID del usuario que actualiza")
):
    """
    Actualiza un registro de recaudo existente.
    """
    try:
        resultado = RecaudoService.actualizar_recaudo(
            id_recaudo=id_recaudo,
            valor_recaudo=Decimal(str(valor_recaudo)) if valor_recaudo else None,
            meta=Decimal(str(meta)) if meta else None,
            id_usuario=id_usuario
        )
        return {
            "success": True,
            "data": resultado,
            "message": "Registro actualizado exitosamente"
        }
    except DatabaseError as e:
        logger.error(f"Error al actualizar recaudo {id_recaudo}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar recaudo: {str(e)}"
        )


@router.delete(
    "/{id_recaudo}",
    summary="Eliminar registro de recaudo",
    description="Elimina lógicamente un registro de recaudo (EsActivo=0)"
)
async def eliminar_recaudo(
    id_recaudo: int,
    id_usuario: int = Query(..., description="ID del usuario que elimina")
):
    """
    Elimina lógicamente un registro de recaudo.
    """
    try:
        resultado = RecaudoService.eliminar_recaudo(id_recaudo, id_usuario)
        return {
            "success": True,
            "data": resultado,
            "message": "Registro eliminado exitosamente"
        }
    except DatabaseError as e:
        logger.error(f"Error al eliminar recaudo {id_recaudo}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar recaudo: {str(e)}"
        )


# =============================================================================
# ENDPOINT DE CARGA DESDE EXCEL/STAGING
# =============================================================================

@router.post(
    "/carga-excel",
    response_model=CargaRecaudoResponse,
    summary="Ejecutar carga desde staging",
    description="Ejecuta SP_CampanasRecaudoQA_CargarDesdeStaging para procesar datos del staging"
)
async def carga_desde_excel(request: CargaDesdeExcelRequest):
    """
    Ejecuta el proceso de carga desde staging.
    
    Asume que los datos ya fueron cargados en CampanasRecaudoStagingQA.
    El SP:
    - Mapea nombres de campañas (Colombia->NPL COL, etc.)
    - Limpia valores numéricos
    - Hace MERGE sobre CampanasRecaudoDiarioQA
    - Registra la carga en CampanasRecaudoCargaQA
    """
    try:
        return CargaRecaudoService.ejecutar_carga_desde_staging(request)
    except DatabaseError as e:
        logger.error(f"Error en carga desde Excel: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en la carga: {str(e)}"
        )


@router.get(
    "/staging/preview",
    summary="Vista previa del staging",
    description="Obtiene una vista previa de los datos cargados en staging"
)
async def preview_staging(
    limite: int = Query(100, description="Número máximo de filas")
):
    """
    Obtiene vista previa de los datos en staging antes de procesarlos.
    """
    try:
        return CargaRecaudoService.obtener_preview_staging(limite)
    except DatabaseError as e:
        logger.error(f"Error al obtener preview de staging: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener preview: {str(e)}"
        )


@router.post(
    "/staging/cargar",
    summary="Cargar datos al staging",
    description="Carga datos al staging para posterior procesamiento"
)
async def cargar_staging(
    filas: List[dict] = Body(..., description="Lista de filas a cargar")
):
    """
    Carga datos a la tabla de staging.
    
    Cada fila debe tener: Campana, AnioMes, DiaHabil, ValorRecaudo, Inversionista, Meta
    """
    try:
        return CargaRecaudoService.cargar_datos_a_staging(filas)
    except DatabaseError as e:
        logger.error(f"Error al cargar staging: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al cargar staging: {str(e)}"
        )
