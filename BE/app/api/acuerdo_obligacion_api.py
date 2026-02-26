from fastapi import APIRouter
from app.bll.acuerdo_obligacion_bll import listar_acuerdos_obligacion

router = APIRouter(prefix="/acuerdos_obligacion", tags=["Acuerdos Obligación"])

@router.get("/")
def obtener_acuerdos_obligacion():
  
    return listar_acuerdos_obligacion()


