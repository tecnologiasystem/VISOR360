from fastapi import APIRouter
from pydantic import BaseModel

from app.bll.usuario_bll import UsuarioBLL

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)



class BuscarCorreoRequest(BaseModel):
    correo: str


class BuscarNombreRequest(BaseModel):
    nombre: str


class LoginRequest(BaseModel):
    correo: str
    clave: str


@router.post("/buscar_correo")
def buscar_por_correo(data: BuscarCorreoRequest):
    return UsuarioBLL.buscar_por_correo(data.correo)


@router.post("/buscar_nombre")
def buscar_por_nombre(data: BuscarNombreRequest):
    return UsuarioBLL.buscar_por_nombre(data.nombre)


@router.post("/login")
def login(data: LoginRequest):
    return UsuarioBLL.login(data.correo, data.clave)
