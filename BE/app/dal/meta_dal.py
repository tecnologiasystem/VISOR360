# DAL para Metas
import pyodbc
from app.database import get_connection1 as get_db_connection_logs
from app.database import get_connection as get_db_connection_export

def obtener_metas_por_pais_mes(id_pais: int, mes: int, anio: int):
    """
    Obtiene todas las metas de un país (campaña grande) para un mes/año específico
    Incluye metas generales del país y metas específicas de subcampañas
    """
    conn = get_db_connection_logs()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            m.IDMeta,
            m.IDPais,
            m.IDCampana,
            c.NombreCampana AS NombreSubcampana,
            m.Mes,
            m.Anio,
            m.MontoMeta,
            m.FechaCreacion,
            m.FechaModificacion
        FROM [LOGS].[dbo].[MetasQA] m
        LEFT JOIN [LOGS].[dbo].[CampanasQA] c ON m.IDCampana = c.IDCampanasQA
        WHERE m.IDPais = ? AND m.Mes = ? AND m.Anio = ?
        ORDER BY CASE WHEN m.IDCampana IS NULL THEN 0 ELSE 1 END, c.NombreCampana
    """
    
    cursor.execute(query, (id_pais, mes, anio))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            "id_meta": row[0],
            "id_pais": row[1],
            "id_campana": row[2],
            "nombre_subcampana": row[3],
            "mes": row[4],
            "anio": row[5],
            "monto_meta": float(row[6]) if row[6] else 0,
            "fecha_creacion": row[7].isoformat() if row[7] else None,
            "fecha_modificacion": row[8].isoformat() if row[8] else None
        })
    
    return result

def obtener_meta_general_pais(id_pais: int, mes: int, anio: int):
    """
    Obtiene la meta general de un país (sin subcampaña específica)
    """
    conn = get_db_connection_logs()
    cursor = conn.cursor()
    
    query = """
        SELECT MontoMeta
        FROM [LOGS].[dbo].[MetasQA]
        WHERE IDPais = ? AND Mes = ? AND Anio = ? AND IDCampana IS NULL
    """
    
    cursor.execute(query, (id_pais, mes, anio))
    row = cursor.fetchone()
    conn.close()
    
    return float(row[0]) if row else 0

def crear_meta(id_pais: int, mes: int, anio: int, monto_meta: float, 
               id_campana: int = None, usuario_creacion: int = None):
    """
    Crea una nueva meta
    """
    conn = get_db_connection_logs()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO [LOGS].[dbo].[MetasQA] 
        (IDPais, IDCampana, Mes, Anio, MontoMeta, UsuarioCreacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    cursor.execute(query, (id_pais, id_campana, mes, anio, monto_meta, usuario_creacion))
    conn.commit()
    
    # Obtener el ID generado
    cursor.execute("SELECT @@IDENTITY")
    new_id = cursor.fetchone()[0]
    conn.close()
    
    return new_id

def actualizar_meta(id_meta: int, monto_meta: float):
    """
    Actualiza el monto de una meta existente
    """
    conn = get_db_connection_logs()
    cursor = conn.cursor()
    
    query = """
        UPDATE [LOGS].[dbo].[MetasQA]
        SET MontoMeta = ?,
            FechaModificacion = GETDATE()
        WHERE IDMeta = ?
    """
    
    cursor.execute(query, (monto_meta, id_meta))
    conn.commit()
    conn.close()
    
    return True

def eliminar_meta(id_meta: int):
    """
    Elimina una meta
    """
    conn = get_db_connection_logs()
    cursor = conn.cursor()
    
    query = "DELETE FROM [LOGS].[dbo].[MetasQA] WHERE IDMeta = ?"
    
    cursor.execute(query, (id_meta,))
    conn.commit()
    conn.close()
    
    return True

def obtener_paises():
    """
    Obtiene la lista de países (campañas grandes)
    """
    conn = get_db_connection_export()
    cursor = conn.cursor()
    
    query = """
        SELECT DISTINCT 
            id_pais,
            nombre_pais_portafolio
        FROM [pais]
        ORDER BY nombre_pais_portafolio
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            "id_pais": row[0],
            "nombre": row[1]
        })
    
    return result
