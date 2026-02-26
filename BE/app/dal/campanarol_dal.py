# DAL para CampanasRolesQA
import pyodbc
from app.database import get_connection1

# CRUD CampanasRolesQA

def crear_campanarol(id_campana, id_rol):
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CampanasRolesQA (IDCampanasQA, IDRol)
        VALUES (?, ?)
    """, (id_campana, id_rol))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def obtener_campanasroles():
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("SELECT IDCampanasRolesQA, IDCampanasQA, IDRol FROM CampanasRolesQA")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "IDCampanasRolesQA": row.IDCampanasRolesQA,
            "IDCampanasQA": row.IDCampanasQA,
            "IDRol": row.IDRol
        }
        for row in rows
    ]


def actualizar_campanarol(id_campanasrolesqa, id_campana, id_rol):
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE CampanasRolesQA SET IDCampanasQA = ?, IDRol = ? WHERE IDCampanasRolesQA = ?
    """, (id_campana, id_rol, id_campanasrolesqa))
    conn.commit()
    cursor.close()
    conn.close()
    return True


def eliminar_campanarol(id_campanasrolesqa):
    conn = get_connection1()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CampanasRolesQA WHERE IDCampanasRolesQA = ?", (id_campanasrolesqa,))
    conn.commit()
    cursor.close()
    conn.close()
    return True
