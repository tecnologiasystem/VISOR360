from fastapi import HTTPException
import bcrypt

from app.dal.usuario_dal import (
    obtener_por_correo,
    obtener_por_nombre,
    obtener_para_login,
)


class UsuarioBLL:

    @staticmethod
    def buscar_por_correo(correo: str):
        usuario = obtener_por_correo(correo)

        if usuario is None:
            raise HTTPException(
                status_code=404, detail="No existe un usuario con ese correo"
            )

        return {
            "UsuarioID": usuario["UsuarioID"],
            "Correo": usuario["Correo"],
            "NombreCompleto": usuario["NombreCompleto"],
        }

    @staticmethod
    def buscar_por_nombre(nombre: str):
        usuario = obtener_por_nombre(nombre)

        if usuario is None:
            raise HTTPException(
                status_code=404, detail="No existe un usuario con ese nombre"
            )

        return {
            "UsuarioID": usuario["UsuarioID"],
            "Correo": usuario["Correo"],
            "NombreCompleto": usuario["NombreCompleto"],
        }

    @staticmethod
    def login(correo: str, clave: str):
        print(f"DEBUG: Intentando login con correo: {correo}")

        usuario = obtener_para_login(correo)

        print(f"DEBUG: Usuario encontrado: {usuario}")

        if usuario is None:
            raise HTTPException(
                status_code=404, detail="Correo o contraseña incorrectos"
            )

        hash_bd = usuario["ClaveHash"]

        print(f"DEBUG: Hash en BD → {hash_bd}")

        # Validar hash bcrypt directamente
        try:
            contraseña_valida = bcrypt.checkpw(
                clave.encode("utf-8"), hash_bd.encode("utf-8")
            )
        except Exception as e:
            print(f"DEBUG: Error al verificar password: {e}")
            raise HTTPException(status_code=400, detail="Error con el hash almacenado")

        if not contraseña_valida:
            raise HTTPException(
                status_code=400, detail="Correo o contraseña incorrectos"
            )

        # Obtener permisos del rol del usuario - BUSCAR POR CORREO
        from app.dal.permisos_dal import obtener_usuario_por_correo
        usuario_completo = obtener_usuario_por_correo(correo)
        
        # Debug: mostrar qué campañas tiene el usuario
        print(f"DEBUG Login - Usuario: {correo}")
        print(f"DEBUG Login - Campañas encontradas: {usuario_completo.get('campanas', []) if usuario_completo else 'None'}")
        print(f"DEBUG Login - Inversionistas encontrados: {usuario_completo.get('inversionistas', []) if usuario_completo else 'None'}")
        
        if not usuario_completo:
            # Si no existe en UsuariosQA, devolver datos básicos
            print(f"DEBUG Login - Usuario NO encontrado en UsuariosQA")
            return {
                "UsuarioID": usuario["UsuarioID"],
                "nombre": usuario.get("NombreCompleto", correo.split('@')[0]),
                "email": correo,
                "rol_nombre": "Usuario",
                "torre_control": False,
                "financiero": False,
                "recursos_humanos": False,
                "gestion_metas": False,
                "gestion_usuarios": False,
                "campanas": [],
                "inversionistas": []
            }
        
        permisos = usuario_completo.get("permisos_modulos", {})
        
        return {
            "UsuarioID": usuario["UsuarioID"],
            "nombre": usuario_completo.get("nombre", ""),
            "email": usuario_completo.get("email", correo),
            "rol_nombre": usuario_completo.get("nombre_rol", ""),
            "torre_control": permisos.get("torre_control", False),
            "financiero": permisos.get("financiero", False),
            "recursos_humanos": permisos.get("recursos_humanos", False),
            "gestion_metas": permisos.get("gestion_metas", False),
            "gestion_usuarios": permisos.get("gestion_usuarios", False),
            "campanas": usuario_completo.get("campanas", []),
            "inversionistas": usuario_completo.get("inversionistas", [])
        }
