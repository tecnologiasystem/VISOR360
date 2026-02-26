from fastapi import HTTPException
from app.dal.rol_dal import (
    obtener_usuario_con_rol_permisos,
    obtener_todos_roles,
    obtener_rol_por_id,
    actualizar_permisos_rol
)


class RolBLL:

    @staticmethod
    def obtener_usuario_permisos(usuario_id: int):
        """
        Obtiene la información del usuario con su rol y permisos de acceso a módulos.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con usuario, rol y permisos de módulos
        """
        usuario = obtener_usuario_con_rol_permisos(usuario_id)

        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if usuario["RolID"] is None:
            raise HTTPException(status_code=400, detail="El usuario no tiene un rol asignado")

        return {
            "usuario": {
                "UsuarioID": usuario["UsuarioID"],
                "Correo": usuario["Correo"],
                "NombreCompleto": usuario["NombreCompleto"]
            },
            "rol": {
                "RolID": usuario["RolID"],
                "NombreRol": usuario["NombreRol"]
            },
            "permisos": {
                "torre_de_control": usuario["TorreDeControl"],
                "financiero": usuario["Financiero"],
                "recursos_humanos": usuario["RecursosHumanos"],
                "metas": usuario["Metas"]
            }
        }

    @staticmethod
    def listar_roles():
        """
        Lista todos los roles disponibles en el sistema.
        
        Returns:
            Lista de roles con sus permisos
        """
        roles = obtener_todos_roles()
        
        return {
            "total_roles": len(roles),
            "roles": roles
        }

    @staticmethod
    def obtener_rol(rol_id: int):
        """
        Obtiene un rol específico por su ID.
        
        Args:
            rol_id: ID del rol
            
        Returns:
            Datos del rol con permisos de módulos
        """
        rol = obtener_rol_por_id(rol_id)

        if rol is None:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        return rol

    @staticmethod
    def actualizar_permisos_rol(rol_id: int, torre_de_control: bool, financiero: bool, recursos_humanos: bool):
        """
        Actualiza los permisos de un rol.
        
        Args:
            rol_id: ID del rol a actualizar
            torre_de_control: True/False para acceso a Torre de Control
            financiero: True/False para acceso a Financiero
            recursos_humanos: True/False para acceso a Recursos Humanos
            
        Returns:
            Rol actualizado
        """
        # Verificar que el rol existe
        rol = obtener_rol_por_id(rol_id)
        if rol is None:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        
        # Actualizar permisos
        actualizado = actualizar_permisos_rol(rol_id, torre_de_control, financiero, recursos_humanos)
        
        if not actualizado:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el rol")
        
        # Devolver rol actualizado
        return obtener_rol_por_id(rol_id)

