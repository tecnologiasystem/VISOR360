"""
Router para Cargas de Recaudo
Endpoints: /cargas
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from bll.carga_bll import CargaRecaudoService
from models.carga import CargaRecaudoListResponse, CargaRecaudo
from models.common import ErrorResponse
from database import DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/cargas",
    tags=["Cargas"],
    responses={
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)


@router.get(
    "/",
    response_model=CargaRecaudoListResponse,
    summary="Historial de cargas",
    description="Obtiene el historial de cargas de recaudo"
)
async def historial_cargas(
    id_usuario: Optional[int] = Query(None, description="Filtrar por usuario"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limite: int = Query(100, description="Número máximo de registros")
):
    """
    Obtiene el historial de cargas de recaudo.
    """
    try:
        return CargaRecaudoService.obtener_historial_cargas(
            id_usuario=id_usuario,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limite=limite
        )
    except DatabaseError as e:
        logger.error(f"Error al obtener historial de cargas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial: {str(e)}"
        )


@router.get(
    "/{id_carga}",
    summary="Obtener carga por ID",
    description="Obtiene los datos de una carga específica"
)
async def obtener_carga(id_carga: int):
    """
    Obtiene una carga por su ID.
    """
    try:
        carga = CargaRecaudoService.obtener_carga_por_id(id_carga)
        if not carga:
            raise HTTPException(
                status_code=404,
                detail=f"Carga con ID {id_carga} no encontrada"
            )
        return {
            "success": True,
            "data": carga.model_dump()
        }
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Error al obtener carga {id_carga}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener carga: {str(e)}"
        )


@router.get(
    "/{id_carga}/registros",
    summary="Registros de una carga",
    description="Obtiene los registros de recaudo asociados a una carga"
)
async def registros_de_carga(id_carga: int):
    """
    Obtiene los registros de recaudo de una carga específica.
    """
    try:
        registros = CargaRecaudoService.obtener_registros_de_carga(id_carga)
        return {
            "success": True,
            "data": registros,
            "total": len(registros),
            "id_carga": id_carga
        }
    except DatabaseError as e:
        logger.error(f"Error al obtener registros de carga {id_carga}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener registros: {str(e)}"
        )


@router.get(
    "/auditoria/",
    summary="Auditoría de cambios",
    description="Obtiene registros de auditoría de cambios en recaudo"
)
async def auditoria_recaudo(
    id_recaudo: Optional[int] = Query(None, description="Filtrar por registro de recaudo"),
    id_carga: Optional[int] = Query(None, description="Filtrar por carga"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limite: int = Query(100, description="Número máximo de registros")
):
    """
    Obtiene registros de auditoría.
    La tabla de auditoría se llena automáticamente por trigger.
    """
    try:
        registros = CargaRecaudoService.obtener_auditoria(
            id_recaudo=id_recaudo,
            id_carga=id_carga,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limite=limite
        )
        return {
            "success": True,
            "data": registros,
            "total": len(registros)
        }
    except DatabaseError as e:
        logger.error(f"Error al obtener auditoría: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener auditoría: {str(e)}"
        )
