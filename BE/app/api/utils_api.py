# API para utilidades (días laborables, etc)
from fastapi import APIRouter, Query, HTTPException
from app.utils.dias_laborables import (
    calcular_dias_laborables,
    obtener_dia_laborable_actual,
    calcular_dias_restantes,
    obtener_fechas_laborables_hasta_hoy
)

router = APIRouter(prefix="/utils", tags=["Utilidades"])

@router.get("/dias-laborables")
def obtener_dias_laborables(
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2020)
):
    """
    Obtiene los días laborables de un mes (L-V sin festivos)
    """
    try:
        total, fechas_obj = calcular_dias_laborables(mes, anio)
        
        # Convertir objetos datetime a strings
        fechas = [f.strftime("%Y-%m-%d") for f in fechas_obj]
        
        return {
            "mes": mes,
            "anio": anio,
            "total_dias": total,
            "fechas": fechas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dia-laborable-actual")
def obtener_dia_actual(
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2020)
):
    """
    Obtiene el número de día laborable actual dentro del mes
    Ejemplo: (10, 22) = "día laborable 10 de 22"
    """
    try:
        dia_actual, total = obtener_dia_laborable_actual(mes, anio)
        dias_restantes = total - dia_actual
        
        return {
            "mes": mes,
            "anio": anio,
            "dia_laborable_actual": dia_actual,
            "total_dias_laborables": total,
            "dias_restantes": dias_restantes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
