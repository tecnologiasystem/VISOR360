from app.dal import permisos_dal
from typing import List, Dict, Optional


# ==================== USUARIOS ====================

def obtener_todos_usuarios():
    """Obtiene todos los usuarios con sus permisos"""
    return permisos_dal.obtener_todos_usuarios()


def obtener_usuario_con_permisos(id_usuario: int):
    """Obtiene un usuario con todos sus permisos detallados"""
    return permisos_dal.obtener_usuario_por_id(id_usuario)


def crear_usuario(nombre: str, email: str, id_rol: int):
    """Crea un nuevo usuario"""
    # Validaciones
    if not nombre or not nombre.strip():
        raise ValueError("El nombre del usuario es requerido")
    
    if not email or not email.strip():
        raise ValueError("El email del usuario es requerido")
    
    if '@' not in email:
        raise ValueError("El email no tiene un formato válido")
    
    if not id_rol or id_rol <= 0:
        raise ValueError("Debe asignar un rol al usuario")
    
    return permisos_dal.crear_usuario(nombre.strip(), email.strip().lower(), id_rol)


def actualizar_usuario(id_usuario: int, nombre: str, email: str, id_rol: int):
    """Actualiza un usuario existente"""
    # Validaciones
    if not id_usuario or id_usuario <= 0:
        raise ValueError("ID de usuario inválido")
    
    if not nombre or not nombre.strip():
        raise ValueError("El nombre del usuario es requerido")
    
    if not email or not email.strip():
        raise ValueError("El email del usuario es requerido")
    
    if '@' not in email:
        raise ValueError("El email no tiene un formato válido")
    
    if not id_rol or id_rol <= 0:
        raise ValueError("Debe asignar un rol al usuario")
    
    return permisos_dal.actualizar_usuario(id_usuario, nombre.strip(), email.strip().lower(), id_rol)


def eliminar_usuario(id_usuario: int):
    """Elimina un usuario"""
    if not id_usuario or id_usuario <= 0:
        raise ValueError("ID de usuario inválido")
    
    return permisos_dal.eliminar_usuario(id_usuario)


# ==================== ROLES ====================

def obtener_todos_roles():
    """Obtiene todos los roles"""
    return permisos_dal.obtener_todos_roles()


def crear_rol(nombre_rol: str, torre_control: bool = False, financiero: bool = False, recursos_humanos: bool = False, gestion_metas: bool = False, gestion_usuarios: bool = False):
    """Crea un nuevo rol"""
    if not nombre_rol or not nombre_rol.strip():
        raise ValueError("El nombre del rol es requerido")
    
    return permisos_dal.crear_rol(nombre_rol.strip(), torre_control, financiero, recursos_humanos, gestion_metas, gestion_usuarios)


def actualizar_rol(id_rol: int, nombre_rol: str, torre_control: bool, financiero: bool, recursos_humanos: bool, gestion_metas: bool, gestion_usuarios: bool):
    """Actualiza un rol existente"""
    if not id_rol or id_rol <= 0:
        raise ValueError("ID de rol inválido")
    
    if not nombre_rol or not nombre_rol.strip():
        raise ValueError("El nombre del rol es requerido")
    
    return permisos_dal.actualizar_rol(id_rol, nombre_rol.strip(), torre_control, financiero, recursos_humanos, gestion_metas, gestion_usuarios)


def eliminar_rol(id_rol: int):
    """Elimina un rol"""
    if not id_rol or id_rol <= 0:
        raise ValueError("ID de rol inválido")
    
    return permisos_dal.eliminar_rol(id_rol)


# ==================== CAMPAÑAS ====================

def obtener_todas_campanas():
    """Obtiene todas las campañas"""
    return permisos_dal.obtener_todas_campanas()


def obtener_campanas_por_rol(id_rol: int):
    """Obtiene las campañas asignadas a un rol"""
    if not id_rol or id_rol <= 0:
        raise ValueError("ID de rol inválido")
    
    return permisos_dal.obtener_campanas_por_rol(id_rol)


def asignar_campana_a_rol(id_campana: int, id_rol: int):
    """Asigna una campaña a un rol"""
    if not id_campana or id_campana <= 0:
        raise ValueError("ID de campaña inválido")
    
    if not id_rol or id_rol <= 0:
        raise ValueError("ID de rol inválido")
    
    return permisos_dal.asignar_campana_a_rol(id_campana, id_rol)


def quitar_campana_de_rol(id_campana: int, id_rol: int):
    """Quita una campaña de un rol"""
    if not id_campana or id_campana <= 0:
        raise ValueError("ID de campaña inválido")
    
    if not id_rol or id_rol <= 0:
        raise ValueError("ID de rol inválido")
    
    return permisos_dal.quitar_campana_de_rol(id_campana, id_rol)


def actualizar_campanas_rol(id_rol: int, ids_campanas: List[int], ids_inversionistas: List[int]):
    """Actualiza las campañas asignadas a un rol basándose en campañas e inversionistas seleccionados"""
    if not id_rol or id_rol <= 0:
        raise ValueError("ID de rol inválido")
    
    if ids_campanas is None:
        ids_campanas = []
    if ids_inversionistas is None:
        ids_inversionistas = []
    
    # Validar que todos los IDs sean válidos
    for id_camp in ids_campanas:
        if not id_camp or id_camp <= 0:
            raise ValueError(f"ID de campaña inválido: {id_camp}")
    
    for id_inv in ids_inversionistas:
        if not id_inv or id_inv <= 0:
            raise ValueError(f"ID de inversionista inválido: {id_inv}")
    
    return permisos_dal.actualizar_campanas_rol(id_rol, ids_campanas, ids_inversionistas)


# ==================== INVERSIONISTAS ====================

def obtener_todos_inversionistas():
    """Obtiene todos los inversionistas"""
    return permisos_dal.obtener_todos_inversionistas()


def obtener_inversionistas_por_campana(id_campana: int):
    """Obtiene los inversionistas de una campaña"""
    if not id_campana or id_campana <= 0:
        raise ValueError("ID de campaña inválido")
    
    return permisos_dal.obtener_inversionistas_por_campana(id_campana)


def obtener_inversionistas_por_rol(id_rol: int):
    """Obtiene todos los inversionistas accesibles para un rol"""
    if not id_rol or id_rol <= 0:
        raise ValueError("ID de rol inválido")
    
    return permisos_dal.obtener_inversionistas_por_rol(id_rol)


# ==================== FUNCIÓN HELPER PARA VALIDAR PERMISOS ====================

def validar_permiso_usuario(id_usuario: int, modulo: str) -> bool:
    """
    Valida si un usuario tiene permiso para un módulo específico
    
    Args:
        id_usuario: ID del usuario
        modulo: 'torre_control', 'financiero', 'recursos_humanos'
    
    Returns:
        bool: True si tiene permiso, False si no
    """
    usuario = permisos_dal.obtener_usuario_por_id(id_usuario)
    
    if not usuario:
        return False
    
    return usuario.get('permisos_modulos', {}).get(modulo, False)


def obtener_campanas_usuario(id_usuario: int) -> List[str]:
    """
    Obtiene las campañas que puede ver un usuario
    
    Returns:
        Lista de nombres de campañas accesibles
    """
    usuario = permisos_dal.obtener_usuario_por_id(id_usuario)
    
    if not usuario:
        return []
    
    return [c['nombre_campana'] for c in usuario.get('campanas', [])]


def obtener_inversionistas_usuario(id_usuario: int) -> List[str]:
    """
    Obtiene los inversionistas que puede ver un usuario
    
    Returns:
        Lista de nombres de inversionistas accesibles
    """
    usuario = permisos_dal.obtener_usuario_por_id(id_usuario)
    
    if not usuario:
        return []
    
    return [i['nombre_inversionista'] for i in usuario.get('inversionistas', [])]
