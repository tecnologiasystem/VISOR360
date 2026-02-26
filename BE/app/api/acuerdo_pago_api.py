from fastapi import APIRouter
from app.bll.acuerdo_pago_bll import listar_acuerdos_pago

router = APIRouter(prefix="/acuerdos_pago", tags=["Acuerdos de Pago"])

@router.get("/")
def obtener_acuerdos_pago():
    """
    Endpoint para obtener todos los acuerdos de pago (máximo 1000 registros)
    """
    return listar_acuerdos_pago()
