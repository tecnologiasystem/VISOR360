from fastapi import APIRouter
from pydantic import BaseModel
from app.bll.rol_bll import RolBLL

router = APIRouter(
    prefix="/roles",
    tags=["Roles y Permisos"]
)


class ActualizarPermisosRequest(BaseModel):
    torre_de_control: bool
    financiero: bool
    recursos_humanos: bool


@router.get("/usuario/{usuario_id}/permisos")
def obtener_permisos_usuario(usuario_id: int):
    """
    Obtiene el usuario con su rol y permisos de acceso a módulos.
    
    Esta es la API principal que devuelve:
    - Información del usuario (UsuarioID, Correo, NombreCompleto)
    - Información del rol (RolID, NombreRol)
    - Permisos de acceso a módulos (torre_de_control, financiero, recursos_humanos)
    
    Args:
        usuario_id: ID del usuario obtenido del login
        
    Returns:
        JSON con usuario, rol y permisos (true/false para cada módulo)
    """
    return RolBLL.obtener_usuario_permisos(usuario_id)


@router.get("/listar")
def listar_roles():
    """
    Lista todos los roles disponibles en el sistema con sus permisos.
    
    Returns:
        Lista de todos los roles con acceso a cada módulo
    """
    return RolBLL.listar_roles()


@router.get("/{rol_id}")
def obtener_rol(rol_id: int):
    """
    Obtiene un rol específico por su ID.
    
    Args:
        rol_id: ID del rol
        
    Returns:
        Datos del rol con permisos de módulos
    """
    return RolBLL.obtener_rol(rol_id)


@router.put("/{rol_id}/permisos")
def actualizar_permisos_rol(rol_id: int, data: ActualizarPermisosRequest):
    """
    Actualiza los permisos de un rol (cambiar acceso a módulos).
    
    Args:
        rol_id: ID del rol a actualizar
        data: Nuevos permisos (true/false para cada módulo)
        
    Returns:
        Rol actualizado con nuevos permisos
    """
    return RolBLL.actualizar_permisos_rol(
        rol_id=rol_id,
        torre_de_control=data.torre_de_control,
        financiero=data.financiero,
        recursos_humanos=data.recursos_humanos
    )
