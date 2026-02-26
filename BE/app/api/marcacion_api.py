from fastapi import APIRouter
from app.bll.marcacion_bll import listar_marcaciones

# Creamos el router con un prefijo y una etiqueta
router = APIRouter(prefix="/marcaciones", tags=["Marcaciones"])

@router.get("/")
def obtener_marcaciones():
    """
    Endpoint que devuelve todas las marcaciones de la base de datos.
    """
    return listar_marcaciones()
