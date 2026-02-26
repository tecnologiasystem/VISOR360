from fastapi import APIRouter
from app.bll.embudo_bll import listar_embudo

router = APIRouter(prefix="/embudo", tags=["Embudo"])

@router.get("/")
def obtener_embudo():
    return listar_embudo()

