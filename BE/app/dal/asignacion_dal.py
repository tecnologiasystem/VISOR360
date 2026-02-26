# dal/asignacion_dal.py
from app.database import get_connection  # Función que devuelve la conexión a la base de datos

def get_asignaciones_top1000():
    """
    Se conecta a la base de datos y obtiene los primeros 1000 registros de la tabla 'asignacion'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP (1000)
            id_asignacion, id_titular, judicializado, fecha_judicializado,
            rango_mora, rango_capital, numero_obligacion, saldo_capital,
            saldo_total, id_vehiculo, id_sucursal, asignación, fecha_asignacion,
            asignacion_anterior, fecha_inicio_asignacion, fecha_fin_asignacion
        FROM asignacion
    """)

    asignaciones = []
    for row in cursor.fetchall():
        asignaciones.append({
            "id_asignacion": row.id_asignacion,
            "id_titular": row.id_titular,
            "judicializado": row.judicializado,
            "fecha_judicializado": row.fecha_judicializado,
            "rango_mora": row.rango_mora,
            "rango_capital": row.rango_capital,
            "numero_obligacion": row.numero_obligacion,
            "saldo_capital": row.saldo_capital,
            "saldo_total": row.saldo_total,
            "id_vehiculo": row.id_vehiculo,
            "id_sucursal": row.id_sucursal,
            "asignación": row.asignación,
            "fecha_asignacion": row.fecha_asignacion,
            "asignacion_anterior": row.asignacion_anterior,
            "fecha_inicio_asignacion": row.fecha_inicio_asignacion,
            "fecha_fin_asignacion": row.fecha_fin_asignacion
        })

    cursor.close()
    conn.close()

    return asignaciones
