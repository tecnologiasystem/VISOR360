from app.database import get_connection

def obtener_todos_los_acuerdos_pago():
    """
    Se conecta a la base de datos y obtiene los primeros 1000 registros
    de la tabla 'acuerdo_pago'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP (1000)
            id_acuerdo_pago, id_acuerdo, periodo_pago,
            valor_pago, numero_acuerdo, anio, mes
        FROM acuerdo_pago
    """)

    acuerdos_pago = []

    for row in cursor.fetchall():
        acuerdos_pago.append({
            "id_acuerdo_pago": row.id_acuerdo_pago,
            "id_acuerdo": row.id_acuerdo,
            "periodo_pago": row.periodo_pago,
            "valor_pago": row.valor_pago,
            "numero_acuerdo": row.numero_acuerdo,
            "anio": row.anio,
            "mes": row.mes
        })

    cursor.close()
    conn.close()
    return acuerdos_pago
