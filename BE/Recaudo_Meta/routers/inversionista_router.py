"""
Router para Inversionistas
Endpoints: /inversionistas
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from bll.inversionista_bll import InversionistaService
from models.inversionista import InversionistaListResponse, InversionistaSimple
from models.common import ErrorResponse
from database import DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inversionistas",
    tags=["Inversionistas"],
    responses={
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)


@router.get(
    "/",
    response_model=InversionistaListResponse,
    summary="Listar todos los inversionistas",
    description="Obtiene la lista de todos los inversionistas disponibles"
)
async def listar_inversionistas(
    solo_activos: bool = Query(True, description="Solo inversionistas activos")
):
    """
    Obtiene todos los inversionistas.
    
    Args:
        solo_activos: Si solo retorna inversionistas activos
    
    Returns:
        Lista de inversionistas
    """
    try:
        return InversionistaService.obtener_todos_inversionistas(solo_activos)
    except DatabaseError as e:
        logger.error(f"Error al listar inversionistas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener inversionistas: {str(e)}"
        )


@router.get(
    "/{id_inversionista}",
    response_model=InversionistaSimple,
    summary="Obtener inversionista por ID",
    description="Obtiene los datos de un inversionista específico"
)
async def obtener_inversionista(id_inversionista: int):
    """
    Obtiene un inversionista por su ID.
    
    Args:
        id_inversionista: ID del inversionista
    
    Returns:
        Datos del inversionista
    """
    try:
        inversionista = InversionistaService.obtener_inversionista_por_id(id_inversionista)
        if not inversionista:
            raise HTTPException(
                status_code=404,
                detail=f"Inversionista con ID {id_inversionista} no encontrado"
            )
        return inversionista
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Error al obtener inversionista {id_inversionista}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener inversionista: {str(e)}"
        )


@router.get(
    "/por-campana/{id_campana}",
    summary="Listar inversionistas por campaña",
    description="Obtiene los inversionistas asociados a una campaña"
)
async def listar_inversionistas_por_campana(
    id_campana: int,
    solo_activos: bool = Query(True, description="Solo inversionistas activos")
):
    """
    Obtiene inversionistas de una campaña.
    
    Args:
        id_campana: ID de la campaña
        solo_activos: Si solo retorna activos
    
    Returns:
        Lista de inversionistas de la campaña
    """
    try:
        inversionistas = InversionistaService.obtener_inversionistas_por_campana(
            id_campana, solo_activos
        )
        return {
            "success": True,
            "data": [i.model_dump() for i in inversionistas],
            "total": len(inversionistas),
            "id_campana": id_campana
        }
    except DatabaseError as e:
        logger.error(f"Error al listar inversionistas de campaña {id_campana}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener inversionistas: {str(e)}"
        )


@router.get(
    "/relaciones/todas",
    summary="Listar todas las relaciones campaña-inversionista",
    description="Obtiene todas las relaciones entre campañas e inversionistas"
)
async def listar_relaciones_campana_inversionista(
    solo_activos: bool = Query(True, description="Solo relaciones activas")
):
    """
    Obtiene todas las relaciones campaña-inversionista.
    
    Returns:
        Lista de relaciones con datos de campaña e inversionista
    """
    try:
        relaciones = InversionistaService.obtener_todas_relaciones_campana_inversionista(
            solo_activos
        )
        return {
            "success": True,
            "data": [r.model_dump() for r in relaciones],
            "total": len(relaciones)
        }
    except DatabaseError as e:
        logger.error(f"Error al listar relaciones: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener relaciones: {str(e)}"
        )


@router.get(
    "/relacion/{id_campana}/{id_inversionista}",
    summary="Obtener relación específica",
    description="Obtiene la relación entre una campaña y un inversionista"
)
async def obtener_relacion(id_campana: int, id_inversionista: int):
    """
    Obtiene una relación específica campaña-inversionista.
    
    Args:
        id_campana: ID de la campaña
        id_inversionista: ID del inversionista
    
    Returns:
        Datos de la relación
    """
    try:
        relacion = InversionistaService.obtener_relacion_campana_inversionista(
            id_campana, id_inversionista
        )
        if not relacion:
            raise HTTPException(
                status_code=404,
                detail=f"Relación campaña {id_campana} - inversionista {id_inversionista} no encontrada"
            )
        return {
            "success": True,
            "data": relacion.model_dump()
        }
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Error al obtener relación: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener relación: {str(e)}"
        )
