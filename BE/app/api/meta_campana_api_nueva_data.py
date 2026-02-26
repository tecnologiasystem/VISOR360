# API Router que usa nueva_data_dal para metas
# Versión completamente separada que no afecta meta_campana_api.py

from fastapi import APIRouter, HTTPException, Query
from app.dal.nueva_data_dal import obtener_meta_pais_nueva_data

router = APIRouter(prefix="/metas-campana", tags=["Metas - Nueva Data"])


@router.get("/pais/{nombre_pais}")
def obtener_meta_por_pais(
    nombre_pais: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
):
    """
    Obtiene la meta total de un país y las metas por subcampaña desde Nueva Data.xlsx
    """
    try:
        resultado = obtener_meta_pais_nueva_data(nombre_pais, mes, anio)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
