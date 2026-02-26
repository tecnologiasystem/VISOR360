from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from app.bll import permisos_bll

router = APIRouter()


# ==================== MODELOS ====================

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    id_rol: int


class UsuarioUpdate(BaseModel):
    nombre: str
    email: EmailStr
    id_rol: int


class RolCreate(BaseModel):
    nombre_rol: str
    torre_control: bool = False
    financiero: bool = False
    recursos_humanos: bool = False
    gestion_metas: bool = False
    gestion_usuarios: bool = False


class RolUpdate(BaseModel):
    nombre_rol: str
    torre_control: bool
    financiero: bool
    recursos_humanos: bool
    gestion_metas: bool
    gestion_usuarios: bool


class AsignarCampanasRol(BaseModel):
    ids_campanas: List[int] = []
    ids_inversionistas: List[int]


# ==================== ENDPOINTS - USUARIOS ====================

@router.get("/usuarios")
def obtener_usuarios():
    """Obtiene todos los usuarios con sus permisos"""
    try:
        usuarios = permisos_bll.obtener_todos_usuarios()
        return {
            "success": True,
            "data": usuarios,
            "count": len(usuarios)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}"
        )


@router.get("/usuarios/{id_usuario}")
def obtener_usuario(id_usuario: int):
    """Obtiene un usuario específico con todos sus permisos"""
    try:
        usuario = permisos_bll.obtener_usuario_con_permisos(id_usuario)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {id_usuario} no encontrado"
            )
        
        return {
            "success": True,
            "data": usuario
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}"
        )


@router.post("/usuarios")
def crear_usuario(usuario: UsuarioCreate):
    """Crea un nuevo usuario"""
    try:
        id_usuario = permisos_bll.crear_usuario(
            nombre=usuario.nombre,
            email=usuario.email,
            id_rol=usuario.id_rol
        )
        
        return {
            "success": True,
            "message": "Usuario creado exitosamente",
            "data": {"id_usuario": id_usuario}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )


@router.put("/usuarios/{id_usuario}")
def actualizar_usuario(id_usuario: int, usuario: UsuarioUpdate):
    """Actualiza un usuario existente"""
    try:
        permisos_bll.actualizar_usuario(
            id_usuario=id_usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            id_rol=usuario.id_rol
        )
        
        return {
            "success": True,
            "message": "Usuario actualizado exitosamente"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}"
        )


@router.delete("/usuarios/{id_usuario}")
def eliminar_usuario(id_usuario: int):
    """Elimina un usuario"""
    try:
        permisos_bll.eliminar_usuario(id_usuario)
        
        return {
            "success": True,
            "message": "Usuario eliminado exitosamente"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar usuario: {str(e)}"
        )


# ==================== ENDPOINTS - ROLES ====================

@router.get("/roles")
def obtener_roles():
    """Obtiene todos los roles"""
    try:
        roles = permisos_bll.obtener_todos_roles()
        return {
            "success": True,
            "data": roles,
            "count": len(roles)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener roles: {str(e)}"
        )


@router.post("/roles")
def crear_rol(rol: RolCreate):
    """Crea un nuevo rol"""
    try:
        id_rol = permisos_bll.crear_rol(
            nombre_rol=rol.nombre_rol,
            torre_control=rol.torre_control,
            financiero=rol.financiero,
            recursos_humanos=rol.recursos_humanos,
            gestion_metas=rol.gestion_metas,
            gestion_usuarios=rol.gestion_usuarios
        )
        
        return {
            "success": True,
            "message": "Rol creado exitosamente",
            "data": {"id_rol": id_rol}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear rol: {str(e)}"
        )


@router.put("/roles/{id_rol}")
def actualizar_rol(id_rol: int, rol: RolUpdate):
    """Actualiza un rol existente"""
    try:
        permisos_bll.actualizar_rol(
            id_rol=id_rol,
            nombre_rol=rol.nombre_rol,
            torre_control=rol.torre_control,
            financiero=rol.financiero,
            recursos_humanos=rol.recursos_humanos,
            gestion_metas=rol.gestion_metas,
            gestion_usuarios=rol.gestion_usuarios
        )
        
        return {
            "success": True,
            "message": "Rol actualizado exitosamente"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar rol: {str(e)}"
        )


@router.delete("/roles/{id_rol}")
def eliminar_rol(id_rol: int):
    """Elimina un rol (solo si no tiene usuarios)"""
    try:
        permisos_bll.eliminar_rol(id_rol)
        
        return {
            "success": True,
            "message": "Rol eliminado exitosamente"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar rol: {str(e)}"
        )


# ==================== ENDPOINTS - CAMPAÑAS ====================

@router.get("/campanas")
def obtener_campanas():
    """Obtiene todas las campañas"""
    try:
        campanas = permisos_bll.obtener_todas_campanas()
        return {
            "success": True,
            "data": campanas,
            "count": len(campanas)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener campañas: {str(e)}"
        )


@router.get("/roles/{id_rol}/campanas")
def obtener_campanas_rol(id_rol: int):
    """Obtiene los inversionistas asignados a un rol (a través de sus campañas)"""
    try:
        inversionistas = permisos_bll.obtener_inversionistas_por_rol(id_rol)
        return {
            "success": True,
            "data": inversionistas,
            "count": len(inversionistas)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener campañas del rol: {str(e)}"
        )


@router.post("/roles/{id_rol}/campanas/{id_campana}")
def asignar_campana_rol(id_rol: int, id_campana: int):
    """Asigna una campaña a un rol"""
    try:
        resultado = permisos_bll.asignar_campana_a_rol(id_campana, id_rol)
        
        if resultado:
            return {
                "success": True,
                "message": "Campaña asignada al rol exitosamente"
            }
        else:
            return {
                "success": True,
                "message": "La campaña ya estaba asignada al rol"
            }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al asignar campaña: {str(e)}"
        )


@router.delete("/roles/{id_rol}/campanas/{id_campana}")
def quitar_campana_rol(id_rol: int, id_campana: int):
    """Quita una campaña de un rol"""
    try:
        permisos_bll.quitar_campana_de_rol(id_campana, id_rol)
        
        return {
            "success": True,
            "message": "Campaña quitada del rol exitosamente"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al quitar campaña: {str(e)}"
        )


@router.put("/roles/{id_rol}/campanas")
def actualizar_campanas_rol(id_rol: int, data: AsignarCampanasRol):
    """Actualiza las campañas asignadas a un rol basándose en campañas e inversionistas seleccionados"""
    try:
        permisos_bll.actualizar_campanas_rol(id_rol, data.ids_campanas, data.ids_inversionistas)
        
        return {
            "success": True,
            "message": f"Campañas actualizadas: {len(data.ids_campanas)} campañas, {len(data.ids_inversionistas)} inversionistas"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar campañas: {str(e)}"
        )


# ==================== ENDPOINTS - INVERSIONISTAS ====================

@router.get("/inversionistas")
def obtener_inversionistas():
    """Obtiene todos los inversionistas"""
    try:
        inversionistas = permisos_bll.obtener_todos_inversionistas()
        return {
            "success": True,
            "data": inversionistas,
            "count": len(inversionistas)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inversionistas: {str(e)}"
        )


@router.get("/campanas/{id_campana}/inversionistas")
def obtener_inversionistas_campana(id_campana: int):
    """Obtiene los inversionistas de una campaña"""
    try:
        inversionistas = permisos_bll.obtener_inversionistas_por_campana(id_campana)
        return {
            "success": True,
            "data": inversionistas,
            "count": len(inversionistas)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inversionistas: {str(e)}"
        )


@router.get("/roles/{id_rol}/inversionistas")
def obtener_inversionistas_rol(id_rol: int):
    """Obtiene los inversionistas accesibles para un rol"""
    try:
        inversionistas = permisos_bll.obtener_inversionistas_por_rol(id_rol)
        return {
            "success": True,
            "data": inversionistas,
            "count": len(inversionistas)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inversionistas: {str(e)}"
        )


# ==================== ENDPOINT - VALIDACIÓN DE PERMISOS ====================

@router.get("/usuarios/{id_usuario}/validar/{modulo}")
def validar_permiso(id_usuario: int, modulo: str):
    """
    Valida si un usuario tiene permiso para un módulo
    
    modulo: 'torre_control', 'financiero', 'recursos_humanos'
    """
    try:
        modulos_validos = ['torre_control', 'financiero', 'recursos_humanos']
        
        if modulo not in modulos_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Módulo inválido. Debe ser uno de: {', '.join(modulos_validos)}"
            )
        
        tiene_permiso = permisos_bll.validar_permiso_usuario(id_usuario, modulo)
        
        return {
            "success": True,
            "data": {
                "id_usuario": id_usuario,
                "modulo": modulo,
                "tiene_permiso": tiene_permiso
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar permiso: {str(e)}"
        )
