from fastapi import APIRouter
from pydantic import BaseModel
from app.bll.campanarol_bll import CampanaRolBLL

router = APIRouter(prefix="/campanasroles", tags=["CampanasRolesQA"])

class CampanaRolRequest(BaseModel):
    id_campana: int
    id_rol: int

@router.post("/")
def crear_campanarol(data: CampanaRolRequest):
    return CampanaRolBLL.crear(data.id_campana, data.id_rol)

@router.get("/")
def listar_campanasroles():
    return CampanaRolBLL.listar()

@router.put("/{id_campanasrolesqa}")
def actualizar_campanarol(id_campanasrolesqa: int, data: CampanaRolRequest):
    return CampanaRolBLL.actualizar(id_campanasrolesqa, data.id_campana, data.id_rol)

@router.delete("/{id_campanasrolesqa}")
def eliminar_campanarol(id_campanasrolesqa: int):
    return CampanaRolBLL.eliminar(id_campanasrolesqa)
