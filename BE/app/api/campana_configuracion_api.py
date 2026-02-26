from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date
from app.bll.campana_configuracion_bll import CampanaConfiguracionBLL

router = APIRouter(prefix="/campanas-configuracion", tags=["CampanaConfiguracionDias"])

class ConfigDayRequest(BaseModel):
    id_campana: int
    fecha: date
    es_habil: bool

class ConfigResponse(BaseModel):
    fecha: date
    es_habil: bool

@router.get("/{id_campana}", response_model=List[ConfigResponse])
def obtener_configuracion(id_campana: int, start_date: date, end_date: date):
    """
    Obtiene la configuración de días para un rango de fechas.
    """
    try:
        data = CampanaConfiguracionBLL.obtener_configuracion(id_campana, start_date, end_date)
        # Map DB result to response model keys if necessary (DAL returns dicts with capitalized keys?)
        # DAL returns "Fecha", "EsHabil". Pydantic expects lowercase usually or we align it.
        # Let's check DAL output again.
        return [
            {"fecha": item["Fecha"], "es_habil": item["EsHabil"]}
            for item in data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def guardar_configuracion(request: ConfigDayRequest):
    """
    Guarda o actualiza la configuración de un día.
    """
    try:
        success = CampanaConfiguracionBLL.guardar_configuracion(request.id_campana, request.fecha, request.es_habil)
        if success:
            return {"message": "Configuración guardada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="No se pudo guardar la configuración")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
