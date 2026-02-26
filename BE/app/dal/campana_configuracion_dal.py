from app.database import get_connection1
from datetime import date

def obtener_configuracion_dias(id_campana: int, start_date: date, end_date: date):
    """
    Obtiene la configuración de días para una campaña en un rango de fechas.
    Retorna una lista de dicts con fecha y es_habil.
    """
    conn = get_connection1()
    cursor = conn.cursor()
    
    query = """
        SELECT Fecha, EsHabil
        FROM CampanaConfiguracionDias
        WHERE IDCampana = ? 
          AND CAST(Fecha AS DATE) >= ? 
          AND CAST(Fecha AS DATE) <= ?
    """
    cursor.execute(query, (id_campana, start_date, end_date))
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Normalizar resultados
    return [
        {
            "Fecha": row.Fecha,
            "EsHabil": bool(row.EsHabil)
        }
        for row in rows
    ]

def guaradar_o_actualizar_configuracion_dia(id_campana: int, fecha: date, es_habil: bool):
    """
    Guarda o actualiza la configuración de un día específico para una campaña.
    """
    conn = get_connection1()
    cursor = conn.cursor()
    
    # Check if exists
    check_query = """
        SELECT ID FROM CampanaConfiguracionDias 
        WHERE IDCampana = ? AND Fecha = ?
    """
    cursor.execute(check_query, (id_campana, fecha))
    row = cursor.fetchone()
    
    if row:
        # Update
        update_query = """
            UPDATE CampanaConfiguracionDias
            SET EsHabil = ?, FechaActualizacion = GETDATE()
            WHERE ID = ?
        """
        cursor.execute(update_query, (es_habil, row.ID))
    else:
        # Insert
        insert_query = """
            INSERT INTO CampanaConfiguracionDias (IDCampana, Fecha, EsHabil)
            VALUES (?, ?, ?)
        """
        cursor.execute(insert_query, (id_campana, fecha, es_habil))
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def obtener_ultimo_estado_por_defecto(id_campana: int):
    """
    (Opcional) Helper para determinar si un día debería ser hábil si no está configurado.
    Por ahora retorna None o lógica por defecto.
    """
    pass
