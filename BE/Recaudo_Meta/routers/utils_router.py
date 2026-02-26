"""
Router de utilidades compatibles con FE
Endpoints: /utils
"""
from fastapi import APIRouter, Query
from typing import List
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/utils",
    tags=["Utilidades"],
)


def obtener_dias_laborables(mes: int, anio: int) -> List[str]:
    """
    Obtiene los días laborables (lunes a viernes) de un mes.
    Retorna lista de fechas en formato ISO (YYYY-MM-DD).
    """
    dias = []
    
    # Primer día del mes
    primer_dia = date(anio, mes, 1)
    
    # Último día del mes
    if mes == 12:
        ultimo_dia = date(anio + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(anio, mes + 1, 1) - timedelta(days=1)
    
    # Iterar por cada día del mes
    dia_actual = primer_dia
    while dia_actual <= ultimo_dia:
        # Lunes=0, Viernes=4 (días laborables)
        if dia_actual.weekday() < 5:
            dias.append(dia_actual.isoformat())
        dia_actual += timedelta(days=1)
    
    return dias


@router.get(
    "/dias-laborables",
    summary="Obtener días laborables del mes",
    description="Retorna lista de días laborables (lunes a viernes) del mes especificado"
)
async def get_dias_laborables(
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2020, description="Año")
):
    """
    Obtiene los días laborables de un mes.
    Usado por el FE para calcular metas diarias.
    """
    try:
        fechas = obtener_dias_laborables(mes, anio)
        return {
            "fechas": fechas,
            "total": len(fechas),
            "mes": mes,
            "anio": anio
        }
    except Exception as e:
        logger.error(f"Error al obtener días laborables: {e}")
        return {
            "fechas": [],
            "total": 0,
            "mes": mes,
            "anio": anio
        }
