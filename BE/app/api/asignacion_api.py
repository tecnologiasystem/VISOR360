from fastapi import APIRouter
from app.bll.asignacion_bll import listar_asignaciones

router = APIRouter(prefix="/asignaciones", tags=["Asignaiones"])

@router.get("/")
def obtener_asignaciones():
    return listar_asignaciones()