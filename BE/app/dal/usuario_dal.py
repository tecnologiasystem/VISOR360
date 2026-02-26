import pyodbc
from app.database import get_connection1



def obtener_por_correo(correo: str):
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UsuarioID, Correo, NombreCompleto, ClaveHash
        FROM Usuario
        WHERE Correo = ?
    """, (correo,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "UsuarioID": row.UsuarioID,
        "Correo": row.Correo,
        "NombreCompleto": row.NombreCompleto,
        "ClaveHash": row.ClaveHash
    }


def obtener_por_nombre(nombre: str):
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UsuarioID, Correo, NombreCompleto
        FROM Usuario
        WHERE NombreCompleto = ?
    """, (nombre,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "UsuarioID": row.UsuarioID,
        "Correo": row.Correo,
        "NombreCompleto": row.NombreCompleto
    }

def obtener_para_login(correo: str):
    conn = get_connection1()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UsuarioID, Correo, ClaveHash
        FROM Usuario
        WHERE Correo = ?
    """, (correo,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
   
    "UsuarioID": row.UsuarioID,
    "Correo": row.Correo,
    "ClaveHash": row.ClaveHash
}

    
    
