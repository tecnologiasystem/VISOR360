from app.database import get_connection

def obtener_todos_los_acuerdos_obligacion():
    """
    Se conecta a la base de datos y obtiene los primeros 1000 registros
    de la tabla 'acuerdo_obligacion'.
    """
    # Conexión con SQL Server
    conn = get_connection()
    cursor = conn.cursor()

    # Consulta SQL
    cursor.execute("""
        SELECT TOP (1000)
            id_acuerdo_obligación, id_acuerdo, id_obligacion, id_titular
        FROM acuerdo_obligacion
    """)

    # Lista donde guardaremos los resultados
    acuerdos_obligacion = []

    # Recorremos cada fila (registro) que vino desde la base de datos
    for row in cursor.fetchall():
        acuerdos_obligacion.append({
            "id_acuerdo_obligación": row.id_acuerdo_obligación,
            "id_acuerdo": row.id_acuerdo,
            "id_obligacion": row.id_obligacion,
            "id_titular": row.id_titular
        })

    # Cerramos conexión y cursor
    cursor.close()
    conn.close()

    # Retornamos la lista con todos los registros
    return acuerdos_obligacion
