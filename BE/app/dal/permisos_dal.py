import pyodbc
from app.database import get_connection1
from typing import List, Dict, Optional


# ==================== USUARIOS ====================

def obtener_todos_usuarios():
    """Obtiene todos los usuarios con sus roles"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            u.IDUsuarioQA,
            u.NombreUsuarioQA,
            u.EmailUsuarioQA,
            u.IDRol,
            r.NombreRol,
            r.TorreDeControl,
            r.Financiero,
            r.RecursosHumanos,
            r.GestionMetas,
            r.GestionUsuarios
        FROM UsuariosQA u
        LEFT JOIN RolQA r ON u.IDRol = r.RolID
        ORDER BY u.NombreUsuarioQA
    """)

    usuarios = []
    for row in cursor.fetchall():
        usuarios.append({
            "id_usuario": row.IDUsuarioQA,
            "nombre": row.NombreUsuarioQA,
            "email": row.EmailUsuarioQA,
            "id_rol": row.IDRol,
            "nombre_rol": row.NombreRol,
            "permisos_modulos": {
                "torre_control": bool(row.TorreDeControl) if row.TorreDeControl is not None else False,
                "financiero": bool(row.Financiero) if row.Financiero is not None else False,
                "recursos_humanos": bool(row.RecursosHumanos) if row.RecursosHumanos is not None else False,
                "gestion_metas": bool(row.GestionMetas) if hasattr(row, 'GestionMetas') and row.GestionMetas is not None else False,
                "gestion_usuarios": bool(row.GestionUsuarios) if hasattr(row, 'GestionUsuarios') and row.GestionUsuarios is not None else False
            }
        })

    cursor.close()
    conn.close()

    return usuarios


def obtener_usuario_por_id_OLD_NO_USAR(id_usuario: int):
    """DEPRECADO - Usaba CampanasInversionistasQA (todos los inversionistas de campaña)
    Ahora usar obtener_usuario_por_id que lee de RolesInversionistasQA"""
    conn = get_connection1()
    cursor = conn.cursor()

    # Datos básicos del usuario
    cursor.execute("""
        SELECT 
            u.IDUsuarioQA,
            u.NombreUsuarioQA,
            u.EmailUsuarioQA,
            u.IDRol,
            r.NombreRol,
            r.TorreDeControl,
            r.Financiero,
            r.RecursosHumanos
        FROM UsuariosQA u
        LEFT JOIN RolQA r ON u.IDRol = r.RolID
        WHERE u.IDUsuarioQA = ?
    """, (id_usuario,))

    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None

    usuario = {
        "id_usuario": row.IDUsuarioQA,
        "nombre": row.NombreUsuarioQA,
        "email": row.EmailUsuarioQA,
        "id_rol": row.IDRol,
        "nombre_rol": row.NombreRol,
        "permisos_modulos": {
            "torre_control": bool(row.TorreDeControl) if row.TorreDeControl is not None else False,
            "financiero": bool(row.Financiero) if row.Financiero is not None else False,
            "recursos_humanos": bool(row.RecursosHumanos) if row.RecursosHumanos is not None else False
        }
    }

    # Campañas asignadas explícitamente al rol
    cursor.execute("""
        SELECT DISTINCT
            c.IDCampanasQA,
            c.NombreCampana
        FROM CampanasRolesQA cr
        INNER JOIN CampanasQA c ON cr.IDCampanasQA = c.IDCampanasQA
        WHERE cr.IDRol = ?
        ORDER BY c.NombreCampana
    """, (row.IDRol,))

    campanas = cursor.fetchall()
    usuario["campanas"] = [
        {"id": r.IDCampanasQA, "nombre": r.NombreCampana, "fechaCreacion": None}
        for r in campanas
    ]

    # Inversionistas: TODOS los de las campañas asignadas
    if campanas:
        ids_campanas = [c.IDCampanasQA for c in campanas]
        placeholders = ','.join('?' * len(ids_campanas))
        cursor.execute(f"""
            SELECT DISTINCT
                i.IDInversionistaQA,
                i.NombreInversionistaQA
            FROM CampanasInversionistasQA ci
            INNER JOIN InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
            WHERE ci.IDCampanasQA IN ({placeholders})
            ORDER BY i.NombreInversionistaQA
        """, tuple(ids_campanas))
        
        usuario["inversionistas"] = [
            {"id_inversionista": r.IDInversionistaQA, "nombre_inversionista": r.NombreInversionistaQA}
            for r in cursor.fetchall()
        ]
    else:
        usuario["inversionistas"] = []

    cursor.close()
    conn.close()

    return usuario


def obtener_usuario_por_id(id_usuario: int):
    """Obtiene un usuario por ID - Lee inversionistas de RolesInversionistasQA"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            u.IDUsuarioQA,
            u.NombreUsuarioQA,
            u.EmailUsuarioQA,
            u.IDRol,
            r.NombreRol,
            r.TorreDeControl,
            r.Financiero,
            r.RecursosHumanos,
            r.GestionMetas,
            r.GestionUsuarios
        FROM UsuariosQA u
        LEFT JOIN RolQA r ON u.IDRol = r.RolID
        WHERE u.IDUsuarioQA = ?
    """, (id_usuario,))

    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None

    usuario = {
        "id_usuario": row.IDUsuarioQA,
        "nombre": row.NombreUsuarioQA,
        "email": row.EmailUsuarioQA,
        "id_rol": row.IDRol,
        "nombre_rol": row.NombreRol,
        "permisos_modulos": {
            "torre_control": bool(row.TorreDeControl) if row.TorreDeControl is not None else False,
            "financiero": bool(row.Financiero) if row.Financiero is not None else False,
            "recursos_humanos": bool(row.RecursosHumanos) if row.RecursosHumanos is not None else False,
            "gestion_metas": bool(row.GestionMetas) if hasattr(row, 'GestionMetas') and row.GestionMetas is not None else False,
            "gestion_usuarios": bool(row.GestionUsuarios) if hasattr(row, 'GestionUsuarios') and row.GestionUsuarios is not None else False
        }
    }

    # Campañas asignadas explícitamente al rol
    cursor.execute("""
        SELECT DISTINCT
            c.IDCampanasQA,
            c.NombreCampana
        FROM CampanasRolesQA cr
        INNER JOIN CampanasQA c ON cr.IDCampanasQA = c.IDCampanasQA
        WHERE cr.IDRol = ?
        ORDER BY c.NombreCampana
    """, (row.IDRol,))

    campanas = cursor.fetchall()
    usuario["campanas"] = [
        {"id": r.IDCampanasQA, "nombre": r.NombreCampana}
        for r in campanas
    ]

    # Inversionistas: Leer SOLO los asignados explícitamente en RolesInversionistasQA
    cursor.execute("""
        SELECT DISTINCT
            i.IDInversionistaQA,
            i.NombreInversionistaQA
        FROM RolesInversionistasQA ri
        INNER JOIN InversionistaQA i ON ri.IDInversionistaQA = i.IDInversionistaQA
        WHERE ri.IDRol = ?
        AND i.EsActivo = 1
        ORDER BY i.NombreInversionistaQA
    """, (row.IDRol,))
    
    usuario["inversionistas"] = [
        {"id_inversionista": r.IDInversionistaQA, "nombre_inversionista": r.NombreInversionistaQA}
        for r in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return usuario


def obtener_usuario_por_correo(correo: str):
    """Obtiene un usuario por su correo electrónico con todos sus permisos"""
    conn = get_connection1()
    cursor = conn.cursor()

    # Datos básicos del usuario buscando por correo
    cursor.execute("""
        SELECT 
            u.IDUsuarioQA,
            u.NombreUsuarioQA,
            u.EmailUsuarioQA,
            u.IDRol,
            r.NombreRol,
            r.TorreDeControl,
            r.Financiero,
            r.RecursosHumanos,
            r.GestionMetas,
            r.GestionUsuarios
        FROM UsuariosQA u
        LEFT JOIN RolQA r ON u.IDRol = r.RolID
        WHERE u.EmailUsuarioQA = ?
    """, (correo,))

    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None

    usuario = {
        "id_usuario": row.IDUsuarioQA,
        "nombre": row.NombreUsuarioQA,
        "email": row.EmailUsuarioQA,
        "id_rol": row.IDRol,
        "nombre_rol": row.NombreRol,
        "permisos_modulos": {
            "torre_control": bool(row.TorreDeControl) if row.TorreDeControl is not None else False,
            "financiero": bool(row.Financiero) if row.Financiero is not None else False,
            "recursos_humanos": bool(row.RecursosHumanos) if row.RecursosHumanos is not None else False,
            "gestion_metas": bool(row.GestionMetas) if hasattr(row, 'GestionMetas') and row.GestionMetas is not None else False,
            "gestion_usuarios": bool(row.GestionUsuarios) if hasattr(row, 'GestionUsuarios') and row.GestionUsuarios is not None else False
        }
    }

    # Campañas asignadas explícitamente al rol
    cursor.execute("""
        SELECT DISTINCT
            c.IDCampanasQA,
            c.NombreCampana
        FROM CampanasRolesQA cr
        INNER JOIN CampanasQA c ON cr.IDCampanasQA = c.IDCampanasQA
        WHERE cr.IDRol = ?
        ORDER BY c.NombreCampana
    """, (row.IDRol,))

    campanas = cursor.fetchall()
    usuario["campanas"] = [
        {"id": r.IDCampanasQA, "nombre": r.NombreCampana}
        for r in campanas
    ]

    # Inversionistas: Leer SOLO los asignados explícitamente en RolesInversionistasQA
    cursor.execute("""
        SELECT DISTINCT
            i.IDInversionistaQA,
            i.NombreInversionistaQA
        FROM RolesInversionistasQA ri
        INNER JOIN InversionistaQA i ON ri.IDInversionistaQA = i.IDInversionistaQA
        WHERE ri.IDRol = ?
        AND i.EsActivo = 1
        ORDER BY i.NombreInversionistaQA
    """, (row.IDRol,))
    
    usuario["inversionistas"] = [
        {"id_inversionista": r.IDInversionistaQA, "nombre_inversionista": r.NombreInversionistaQA}
        for r in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return usuario


# Alias para compatibilidad con el login - ahora usa correo
obtener_usuario_con_permisos = obtener_usuario_por_id


def crear_usuario(nombre: str, email: str, id_rol: int):
    """Crea un nuevo usuario"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO UsuariosQA (NombreUsuarioQA, EmailUsuarioQA, IDRol)
        VALUES (?, ?, ?)
    """, (nombre, email, id_rol))

    conn.commit()
    
    # Obtener el ID del usuario recién creado
    cursor.execute("SELECT @@IDENTITY AS id")
    id_usuario = cursor.fetchone().id

    cursor.close()
    conn.close()

    return id_usuario


def actualizar_usuario(id_usuario: int, nombre: str, email: str, id_rol: int):
    """Actualiza un usuario existente"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE UsuariosQA
        SET NombreUsuarioQA = ?,
            EmailUsuarioQA = ?,
            IDRol = ?
        WHERE IDUsuarioQA = ?
    """, (nombre, email, id_rol, id_usuario))

    conn.commit()
    cursor.close()
    conn.close()

    return True


def eliminar_usuario(id_usuario: int):
    """Elimina un usuario"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM UsuariosQA WHERE IDUsuarioQA = ?", (id_usuario,))

    conn.commit()
    cursor.close()
    conn.close()

    return True


# ==================== ROLES ====================

def obtener_todos_roles():
    """Obtiene todos los roles disponibles"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            RolID,
            NombreRol,
            TorreDeControl,
            Financiero,
            RecursosHumanos,
            GestionMetas,
            GestionUsuarios,
            FechaCreacion
            FechaCreacion
        FROM RolQA
        ORDER BY NombreRol
    """)

    roles = []
    for row in cursor.fetchall():
        roles.append({
            "id_rol": row.RolID,
            "nombre_rol": row.NombreRol,
            "torre_control": bool(row.TorreDeControl),
            "financiero": bool(row.Financiero),
            "recursos_humanos": bool(row.RecursosHumanos),
            "gestion_metas": bool(row.GestionMetas) if hasattr(row, 'GestionMetas') and row.GestionMetas is not None else False,
            "gestion_usuarios": bool(row.GestionUsuarios) if hasattr(row, 'GestionUsuarios') and row.GestionUsuarios is not None else False,
            "fecha_creacion": row.FechaCreacion.isoformat() if row.FechaCreacion else None
        })

    cursor.close()
    conn.close()

    return roles


def crear_rol(nombre_rol: str, torre_control: bool, financiero: bool, recursos_humanos: bool, gestion_metas: bool, gestion_usuarios: bool):
    """Crea un nuevo rol"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO RolQA (NombreRol, TorreDeControl, Financiero, RecursosHumanos, GestionMetas, GestionUsuarios)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre_rol, int(torre_control), int(financiero), int(recursos_humanos), int(gestion_metas), int(gestion_usuarios)))

    conn.commit()
    
    cursor.execute("SELECT @@IDENTITY AS id")
    id_rol = cursor.fetchone().id

    cursor.close()
    conn.close()

    return id_rol


def actualizar_rol(id_rol: int, nombre_rol: str, torre_control: bool, financiero: bool, recursos_humanos: bool, gestion_metas: bool, gestion_usuarios: bool):
    """Actualiza un rol existente"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE RolQA
        SET NombreRol = ?,
            TorreDeControl = ?,
            Financiero = ?,
            RecursosHumanos = ?,
            GestionMetas = ?,
            GestionUsuarios = ?
        WHERE RolID = ?
    """, (nombre_rol, int(torre_control), int(financiero), int(recursos_humanos), int(gestion_metas), int(gestion_usuarios), id_rol))

    conn.commit()
    cursor.close()
    conn.close()

    return True


def eliminar_rol(id_rol: int):
    """Elimina un rol (solo si no tiene usuarios asignados)"""
    conn = get_connection1()
    cursor = conn.cursor()

    # Verificar si hay usuarios con este rol
    cursor.execute("SELECT COUNT(*) as total FROM UsuariosQA WHERE IDRol = ?", (id_rol,))
    count = cursor.fetchone().total

    if count > 0:
        cursor.close()
        conn.close()
        raise ValueError(f"No se puede eliminar el rol porque tiene {count} usuario(s) asignado(s)")

    cursor.execute("DELETE FROM RolQA WHERE RolID = ?", (id_rol,))

    conn.commit()
    cursor.close()
    conn.close()

    return True


# ==================== CAMPAÑAS ====================

def obtener_todas_campanas():
    """Obtiene todas las campañas"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.IDCampanasQA,
            c.NombreCampana,
            c.FechaCreacion,
            c.IDUsuarioLider,
            u.NombreUsuarioQA as NombreLider
        FROM CampanasQA c
        LEFT JOIN UsuariosQA u ON c.IDUsuarioLider = u.IDUsuarioQA
        ORDER BY c.NombreCampana
    """)

    campanas = []
    for row in cursor.fetchall():
        campanas.append({
            "id_campana": row.IDCampanasQA,
            "nombre_campana": row.NombreCampana,
            "fecha_creacion": row.FechaCreacion.isoformat() if row.FechaCreacion else None,
            "id_usuario_lider": row.IDUsuarioLider,
            "nombre_lider": row.NombreLider
        })

    cursor.close()
    conn.close()

    return campanas


def obtener_campanas_por_rol(id_rol: int):
    """Obtiene las campañas asignadas a un rol"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.IDCampanasQA,
            c.NombreCampana
        FROM CampanasRolesQA cr
        INNER JOIN CampanasQA c ON cr.IDCampanasQA = c.IDCampanasQA
        WHERE cr.IDRol = ?
        ORDER BY c.NombreCampana
    """, (id_rol,))

    campanas = [
        {"id_campana": row.IDCampanasQA, "nombre_campana": row.NombreCampana}
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return campanas


def asignar_campana_a_rol(id_campana: int, id_rol: int):
    """Asigna una campaña a un rol"""
    conn = get_connection1()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO CampanasRolesQA (IDCampanasQA, IDRol)
            VALUES (?, ?)
        """, (id_campana, id_rol))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except pyodbc.IntegrityError:
        # Ya existe esta asignación
        cursor.close()
        conn.close()
        return False


def quitar_campana_de_rol(id_campana: int, id_rol: int):
    """Quita una campaña de un rol"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM CampanasRolesQA
        WHERE IDCampanasQA = ? AND IDRol = ?
    """, (id_campana, id_rol))

    conn.commit()
    cursor.close()
    conn.close()

    return True


def actualizar_campanas_rol(id_rol: int, ids_campanas: List[int], ids_inversionistas: List[int]):
    """Actualiza las campañas asignadas a un rol - usa directamente ids_campanas"""
    conn = get_connection1()
    cursor = conn.cursor()

    try:
        print(f"DEBUG actualizar_campanas_rol - Rol: {id_rol}")
        print(f"  - Campañas a guardar: {ids_campanas}")
        print(f"  - Inversionistas a guardar: {ids_inversionistas}")
        
        # Eliminar asignaciones actuales de campañas
        cursor.execute("DELETE FROM CampanasRolesQA WHERE IDRol = ?", (id_rol,))
        deleted_campanas = cursor.rowcount
        print(f"DEBUG - Eliminadas {deleted_campanas} campañas anteriores")

        # Eliminar asignaciones actuales de inversionistas
        cursor.execute("DELETE FROM RolesInversionistasQA WHERE IDRol = ?", (id_rol,))
        deleted_inversionistas = cursor.rowcount
        print(f"DEBUG - Eliminados {deleted_inversionistas} inversionistas anteriores")

        # Insertar las campañas
        if ids_campanas:
            for id_camp in ids_campanas:
                print(f"DEBUG - Insertando campaña {id_camp}")
                cursor.execute("""
                    INSERT INTO CampanasRolesQA (IDCampanasQA, IDRol)
                    VALUES (?, ?)
                """, (id_camp, id_rol))

        # Insertar los inversionistas
        if ids_inversionistas:
            for id_inv in ids_inversionistas:
                print(f"DEBUG - Insertando inversionista {id_inv}")
                cursor.execute("""
                    INSERT INTO RolesInversionistasQA (IDRol, IDInversionistaQA, FechaCreacion)
                    VALUES (?, ?, GETDATE())
                """, (id_rol, id_inv))

        conn.commit()
        print(f"DEBUG - Commit exitoso:")
        print(f"  - Campañas guardadas: {len(ids_campanas) if ids_campanas else 0}")
        print(f"  - Inversionistas guardados: {len(ids_inversionistas) if ids_inversionistas else 0}")
        
        # Verificar que se guardaron
        cursor.execute("SELECT IDCampanasQA FROM CampanasRolesQA WHERE IDRol = ?", (id_rol,))
        guardadas_campanas = [row.IDCampanasQA for row in cursor.fetchall()]
        print(f"DEBUG - Campañas en BD: {guardadas_campanas}")
        
        cursor.execute("SELECT IDInversionistaQA FROM RolesInversionistasQA WHERE IDRol = ?", (id_rol,))
        guardados_inversionistas = [row.IDInversionistaQA for row in cursor.fetchall()]
        print(f"DEBUG - Inversionistas en BD: {guardados_inversionistas}")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"ERROR en actualizar_campanas_rol: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        raise


# ==================== INVERSIONISTAS ====================

def obtener_todos_inversionistas():
    """Obtiene todos los inversionistas con su campaña asociada (sin duplicados)"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT
            i.IDInversionistaQA,
            i.NombreInversionistaQA,
            i.EsActivo,
            i.FechaCreacion,
            c.NombreCampana
        FROM InversionistaQA i
        LEFT JOIN CampanasInversionistasQA ci ON i.IDInversionistaQA = ci.IDInversionistaQA
        LEFT JOIN CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        WHERE i.EsActivo = 1
        ORDER BY c.NombreCampana, i.NombreInversionistaQA
    """)

    inversionistas = []
    for row in cursor.fetchall():
        inversionistas.append({
            "id_inversionista": row.IDInversionistaQA,
            "nombre_inversionista": row.NombreInversionistaQA,
            "es_activo": bool(row.EsActivo),
            "fecha_creacion": row.FechaCreacion.isoformat() if row.FechaCreacion else None,
            "nombre_campana": row.NombreCampana
        })

    cursor.close()
    conn.close()

    return inversionistas


def obtener_inversionistas_por_campana(id_campana: int):
    """Obtiene los inversionistas de una campaña"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            i.IDInversionistaQA,
            i.NombreInversionistaQA
        FROM CampanasInversionistasQA ci
        INNER JOIN InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        WHERE ci.IDCampanasQA = ?
        ORDER BY i.NombreInversionistaQA
    """, (id_campana,))

    inversionistas = [
        {"id_inversionista": row.IDInversionistaQA, "nombre_inversionista": row.NombreInversionistaQA}
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return inversionistas


def obtener_inversionistas_por_rol(id_rol: int):
    """Obtiene los inversionistas específicos asignados a un rol"""
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT
            i.IDInversionistaQA,
            i.NombreInversionistaQA,
            i.EsActivo
        FROM RolesInversionistasQA ri
        INNER JOIN InversionistaQA i ON ri.IDInversionistaQA = i.IDInversionistaQA
        WHERE ri.IDRol = ?
        ORDER BY i.NombreInversionistaQA
    """, (id_rol,))

    inversionistas = [
        {
            "id_inversionista": row.IDInversionistaQA,
            "nombre_inversionista": row.NombreInversionistaQA,
            "es_activo": bool(row.EsActivo)
        }
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return inversionistas
