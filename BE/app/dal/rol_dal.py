import pyodbc
from app.database import get_connection1


def obtener_usuario_con_rol_permisos(usuario_id: int):
    """
    Obtiene el usuario con su rol y permisos de acceso a módulos.
    
    Args:
        usuario_id: ID del usuario
        
    Returns:
        Diccionario con información del usuario, rol y acceso a módulos
    """
    conn = get_connection1()
    cursor = conn.cursor()

    # Obtener datos del usuario y su rol con permisos
    cursor.execute("""
        SELECT 
            u.IDUsuarioQA,
            u.EmailUsuarioQA,
            u.NombreUsuarioQA,
            u.IDRol,
            r.NombreRol,
            r.TorreDeControl,
            r.Financiero,
            r.RecursosHumanos,
            r.Metas
        FROM [LOGS].[dbo].[UsuariosQA] u
        LEFT JOIN [LOGS].[dbo].[RolQA] r ON u.IDRol = r.RolID
        WHERE u.IDUsuarioQA = ?
    """, (usuario_id,))

    usuario_row = cursor.fetchone()

    cursor.close()
    conn.close()

    if usuario_row is None:
        return None

    return {
        "UsuarioID": usuario_row[0],  # IDUsuarioQA
        "Correo": usuario_row[1],
        "NombreCompleto": usuario_row[2],
        "RolID": usuario_row[3],  # IDRol
        "NombreRol": usuario_row[4] if usuario_row[4] else None,
        "TorreDeControl": bool(usuario_row[5]) if usuario_row[5] is not None else False,
        "Financiero": bool(usuario_row[6]) if usuario_row[6] is not None else False,
        "RecursosHumanos": bool(usuario_row[7]) if usuario_row[7] is not None else False,
        "Metas": bool(usuario_row[8]) if usuario_row[8] is not None else False
    }


def obtener_todos_roles():
    """
    Obtiene todos los roles disponibles en el sistema.
    
    Returns:
        Lista de roles con sus permisos de módulos
    """
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            RolID, 
            NombreRol, 
            TorreDeControl,
            Financiero,
            RecursosHumanos,
            Metas,
            FechaCreacion
        FROM [LOGS].[dbo].[RolQA]
        ORDER BY NombreRol
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "RolID": row.RolID,
            "NombreRol": row.NombreRol,
            "TorreDeControl": bool(row.TorreDeControl),
            "Financiero": bool(row.Financiero),
            "RecursosHumanos": bool(row.RecursosHumanos),
            "Metas": bool(row.Metas),
            "FechaCreacion": str(row.FechaCreacion)
        }
        for row in rows
    ]


def obtener_rol_por_id(rol_id: int):
    """
    Obtiene un rol específico por su ID.
    
    Args:
        rol_id: ID del rol
        
    Returns:
        Datos del rol con permisos de módulos
    """
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            RolID, 
            NombreRol, 
            TorreDeControl,
            Financiero,
            RecursosHumanos,
            Metas,
            FechaCreacion
        FROM [LOGS].[dbo].[RolQA]
        WHERE RolID = ?
    """, (rol_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "RolID": row.RolID,
        "NombreRol": row.NombreRol,
        "TorreDeControl": bool(row.TorreDeControl),
        "Financiero": bool(row.Financiero),
        "RecursosHumanos": bool(row.RecursosHumanos),
        "Metas": bool(row.Metas),
        "FechaCreacion": str(row.FechaCreacion)
    }


def actualizar_permisos_rol(rol_id: int, torre_de_control: bool, financiero: bool, recursos_humanos: bool):
    """
    Actualiza los permisos de acceso a módulos de un rol.
    
    Args:
        rol_id: ID del rol a actualizar
        torre_de_control: True para dar acceso, False para quitar
        financiero: True para dar acceso, False para quitar
        recursos_humanos: True para dar acceso, False para quitar
        
    Returns:
        True si se actualizó correctamente
    """
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE [LOGS].[dbo].[RolQA]
        SET TorreDeControl = ?,
            Financiero = ?,
            RecursosHumanos = ?
        WHERE RolID = ?
    """, (1 if torre_de_control else 0, 
          1 if financiero else 0, 
          1 if recursos_humanos else 0, 
          rol_id))

    rows_affected = cursor.rowcount
    conn.commit()

    cursor.close()
    conn.close()

    return rows_affected > 0


