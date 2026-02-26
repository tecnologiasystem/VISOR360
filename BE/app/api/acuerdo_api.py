
from fastapi import APIRouter
from app.bll.acuerdo_bll import listar_acuerdos

# Definimos el router con el prefijo y tags
router = APIRouter(prefix="/acuerdos", tags=["Acuerdo"])

# Ruta interna **sin repetir el prefijo**
@router.get("/")  # Se accederá como /acuerdo_decisio/
def obtener_acuerdos():
    return listar_acuerdos()


