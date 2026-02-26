from fastapi import APIRouter
from pydantic import BaseModel
from app.bll.campana_bll import CampanaBLL

router = APIRouter(prefix="/campanas", tags=["CampanasQA"])

class CampanaRequest(BaseModel):
    nombre: str
    id_usuario_lider: int

@router.post("/")
def crear_campana(data: CampanaRequest):
    return CampanaBLL.crear(data.nombre, data.id_usuario_lider)

@router.get("/")
def listar_campanas():
    return CampanaBLL.listar()

@router.put("/{id_campana}")
def actualizar_campana(id_campana: int, data: CampanaRequest):
    return CampanaBLL.actualizar(id_campana, data.nombre, data.id_usuario_lider)

@router.delete("/{id_campana}")
def eliminar_campana(id_campana: int):
    return CampanaBLL.eliminar(id_campana)

@router.get("/usuario/{id_usuario}")
def listar_campanas_por_usuario(id_usuario: int):
    return CampanaBLL.listar_por_usuario(id_usuario)
