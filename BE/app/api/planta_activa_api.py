"""
API para Radar de Talento Humano - Planta Activa.
Endpoints para consultar estadísticas de empleados por país.
"""

from fastapi import APIRouter, Query, HTTPException
from app.bll.planta_activa_bll import (
    obtener_resumen_completo,
    obtener_lista_paises
)
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/planta-activa", tags=["Planta Activa"])


@router.get("/resumen")
def get_resumen(
    pais: Optional[str] = Query(None, description="COLOMBIA, PERU, PANAMA o vacío para TODOS"),
    mes: Optional[int] = Query(None, ge=1, le=12, description="Mes de corte (1-12)"),
    anio: Optional[int] = Query(None, ge=2020, description="Año de corte")
):
    """
    Obtiene el resumen de planta activa.
    Filtra por fecha_corte si se especifica mes/año.
    
    Returns:
    - personal_activo: Total de empleados (card 1)
    - costo_recurso_humano: Suma de salarios (card 2)
    - generos: {genero: cantidad} (card 3)
    - edad_promedio: Edad promedio (card 4)
    """
    try:
        resultado = obtener_resumen_completo(pais, mes, anio)
        return {
            "success": True,
            "data": resultado,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paises")
def get_paises():
    """
    Obtiene la lista de países disponibles.
    """
    try:
        paises = obtener_lista_paises()
        return {
            "success": True,
            "paises": paises
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pais/{pais}")
def get_por_pais(
    pais: str,
    mes: Optional[int] = Query(None, ge=1, le=12, description="Mes de corte (1-12)"),
    anio: Optional[int] = Query(None, ge=2020, description="Año de corte")
):
    """
    Obtiene estadísticas de un país específico.
    Filtra por fecha_corte si se especifica mes/año.
    """
    try:
        resultado = obtener_resumen_completo(pais, mes, anio)
        return {
            "success": True,
            "data": resultado,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

