from fastapi import APIRouter
from app.bll.acuerdo_decision_bll import listar_acuerdo_decisiones

router = APIRouter(prefix="/acuerdo_decisiones", tags=["Acuerdo Decisiones"])

@router.get("/")
def obtener_acuerdo_decisiones():
    return listar_acuerdo_decisiones()
