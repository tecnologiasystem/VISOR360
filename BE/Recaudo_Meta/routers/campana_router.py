"""
Router para Campañas
Endpoints: /campanas
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from bll.campana_bll import CampanaService
from models.campana import CampanaListResponse, CampanaSimple
from models.common import ErrorResponse
from database import DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/campanas",
    tags=["Campañas"],
    responses={
        500: {"model": ErrorResponse, "description": "Error interno del servidor"}
    }
)


@router.get(
    "/",
    response_model=CampanaListResponse,
    summary="Listar todas las campañas",
    description="Obtiene la lista de todas las campañas disponibles para selectores en el FE"
)
async def listar_campanas():
    """
    Obtiene todas las campañas.
    
    Returns:
        Lista de campañas con ID y nombre
    """
    try:
        return CampanaService.obtener_todas_campanas()
    except DatabaseError as e:
        logger.error(f"Error al listar campañas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener campañas: {str(e)}"
        )


@router.get(
    "/{id_campana}",
    response_model=CampanaSimple,
    summary="Obtener campaña por ID",
    description="Obtiene los datos de una campaña específica"
)
async def obtener_campana(id_campana: int):
    """
    Obtiene una campaña por su ID.
    
    Args:
        id_campana: ID de la campaña
    
    Returns:
        Datos de la campaña
    """
    try:
        campana = CampanaService.obtener_campana_por_id(id_campana)
        if not campana:
            raise HTTPException(
                status_code=404,
                detail=f"Campaña con ID {id_campana} no encontrada"
            )
        return campana
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Error al obtener campaña {id_campana}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener campaña: {str(e)}"
        )


@router.get(
    "/con-inversionistas/",
    summary="Listar campañas con sus inversionistas",
    description="Obtiene las campañas agrupadas con sus inversionistas asociados"
)
async def listar_campanas_con_inversionistas():
    """
    Obtiene campañas con sus inversionistas asociados.
    
    Returns:
        Lista de campañas, cada una con su lista de inversionistas
    """
    try:
        datos = CampanaService.obtener_campanas_con_inversionistas()
        return {
            "success": True,
            "data": datos,
            "total": len(datos)
        }
    except DatabaseError as e:
        logger.error(f"Error al listar campañas con inversionistas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos: {str(e)}"
        )


@router.get(
    "/por-rol/{id_rol}",
    summary="Listar campañas por rol",
    description="Obtiene las campañas asociadas a un rol específico"
)
async def listar_campanas_por_rol(id_rol: int):
    """
    Obtiene campañas de un rol.
    
    Args:
        id_rol: ID del rol
    
    Returns:
        Lista de campañas del rol
    """
    try:
        campanas = CampanaService.obtener_campanas_por_rol(id_rol)
        return {
            "success": True,
            "data": [c.model_dump() for c in campanas],
            "total": len(campanas)
        }
    except DatabaseError as e:
        logger.error(f"Error al listar campañas por rol {id_rol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener campañas: {str(e)}"
        )
