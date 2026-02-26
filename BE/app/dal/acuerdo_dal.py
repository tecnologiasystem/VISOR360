from app.database import get_connection

def obtener_todos_los_acuerdos():
    """
    Obtiene los primeros 1000 registros de la tabla 'acuerdo'
    desde la base de datos export_planeacion.dbo.acuerdo.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP (1000)
            id_acuerdo,
            numero_acuerdo,
            id_tipo_acuerdo,
            id_estado_acuerdo,
            saldo_capital,
            numero_cuotas,
            valor_total_acuerdo,
            valor_recaudo_mes,
            valor_recaudo_acuerdo,
            fecha_creacion_acuerdo,
            fecha_inicio_mora,
            id_sucursal,
            id_vehiculo,
            id_asesor,
            id_unidad_denominacion,
            saldo_total,
            fecha_primera_cuota,
            id_titular,
            observacion,
            id_pais,
            cantidad_obligaciones
        FROM acuerdo
    """)

    acuerdos = []
    for row in cursor.fetchall():
        acuerdos.append({
            "id_acuerdo": row.id_acuerdo,
            "numero_acuerdo": row.numero_acuerdo,
            "id_tipo_acuerdo": row.id_tipo_acuerdo,
            "id_estado_acuerdo": row.id_estado_acuerdo,
            "saldo_capital": row.saldo_capital,
            "numero_cuotas": row.numero_cuotas,
            "valor_total_acuerdo": row.valor_total_acuerdo,
            "valor_recaudo_mes": row.valor_recaudo_mes,
            "valor_recaudo_acuerdo": row.valor_recaudo_acuerdo,
            "fecha_creacion_acuerdo": row.fecha_creacion_acuerdo,
            "fecha_inicio_mora": row.fecha_inicio_mora,
            "id_sucursal": row.id_sucursal,
            "id_vehiculo": row.id_vehiculo,
            "id_asesor": row.id_asesor,
            "id_unidad_denominacion": row.id_unidad_denominacion,
            "saldo_total": row.saldo_total,
            "fecha_primera_cuota": row.fecha_primera_cuota,
            "id_titular": row.id_titular,
            "observacion": row.observacion,
            "id_pais": row.id_pais,
            "cantidad_obligaciones": row.cantidad_obligaciones
        })

    cursor.close()
    conn.close()
    return acuerdos
