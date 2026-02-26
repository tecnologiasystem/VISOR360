# API Router que usa nueva_data_dal para recaudos
# Versión completamente separada que no afecta recaudo_api.py

from fastapi import APIRouter, Query, HTTPException
from app.dal.nueva_data_dal import obtener_recaudo_pais_nueva_data

router = APIRouter(prefix="/recaudos", tags=["Recaudos - Nueva Data"])


@router.get("/pais_by_name/{pais_name}")
def obtener_recaudo_por_pais_name(
    pais_name: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
):
    """
    Endpoint que obtiene recaudo por nombre de país desde Nueva Data.xlsx
    """
    try:
        return obtener_recaudo_pais_nueva_data(pais_name, mes, anio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pais_by_name/{pais_name}/campanas")
def obtener_campanas_por_pais_name(
    pais_name: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
):
    """
    Obtiene las subcampañas (inversionistas) de un país
    """
    try:
        result = obtener_recaudo_pais_nueva_data(pais_name, mes, anio)
        return result.get("subcampanas", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
