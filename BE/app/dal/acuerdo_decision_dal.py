from app.database import get_connection

def obtener_acuerdo_decisiones_db():
    """
    Se conecta a la base de datos y obtiene los primeros 1000 registros
    de la tabla 'acuerdo_decision'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP (1000)
            id_acuerdo_decision, id_acuerdo, id_agente,
            fecha_creacion, decision, numero_instancia
        FROM acuerdo_decision
    """)

    decisiones = []
    for row in cursor.fetchall():
        decisiones.append({
            "id_acuerdo_decision": row.id_acuerdo_decision,
            "id_acuerdo": row.id_acuerdo,
            "id_agente": row.id_agente,
            "fecha_creacion": row.fecha_creacion,
            "decision": row.decision,
            "numero_instancia": row.numero_instancia
        })

    cursor.close()
    conn.close()
    return decisiones
