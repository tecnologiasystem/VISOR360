# DAL para CampanasQA
import pyodbc
from app.database import get_connection1

# CRUD CampanasQA

def crear_campana(nombre, id_usuario_lider):
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CampanasQA (NombreCampana, IDUsuarioLider)
        VALUES (?, ?)
    """, (nombre, id_usuario_lider))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def obtener_campanas():
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("SELECT IDCampanasQA, NombreCampana, FechaCreacion, IDUsuarioLider FROM CampanasQA")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "IDCampanasQA": row.IDCampanasQA,
            "NombreCampana": row.NombreCampana,
            "FechaCreacion": str(row.FechaCreacion),
            "IDUsuarioLider": row.IDUsuarioLider
        }
        for row in rows
    ]


def actualizar_campana(id_campana, nombre, id_usuario_lider):
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE CampanasQA SET NombreCampana = ?, IDUsuarioLider = ? WHERE IDCampanasQA = ?
    """, (nombre, id_usuario_lider, id_campana))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def eliminar_campana(id_campana):
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CampanasQA WHERE IDCampanasQA = ?", (id_campana,))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def obtener_campanas_por_usuario(id_usuario):
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.IDCampanasQA, c.NombreCampana, c.FechaCreacion
        FROM [LOGS].[dbo].[CampanasQA] c
        INNER JOIN [LOGS].[dbo].[CampanasRolesQA] cr ON c.IDCampanasQA = cr.IDCampanasQA
        INNER JOIN [LOGS].[dbo].[UsuariosQA] u ON cr.IDRol = u.IDRol
        WHERE u.IDUsuarioQA = ?
    """, (id_usuario,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "IDCampanasQA": row.IDCampanasQA,
            "NombreCampana": row.NombreCampana,
            "FechaCreacion": str(row.FechaCreacion) if row.FechaCreacion else None
        }
        for row in rows
    ]
