# dal/embudo_dal.py
from app.database import get_connection  # Esta función la tienes que tener ya lista

def get_embudo_top1000():
    """
    Se conecta a la base de datos y obtiene los primeros 1000 registros de la tabla 'embudo_mes'.
    """
    conn = get_connection()

    cursor = conn.cursor()

    # Ejecutamos la consulta SQL
    cursor.execute("""
        SELECT TOP (1000)
            id_titular, id_sucursal, id_estado_obligacion, es_fallecido,
            judicializado, saldo_capital, saldo_capital_consolidado,
            porcentaje_participacion, id_estado_reporte_cifin, id_estado_reporte_datacredito,
            id_originador, id_inversionista, id_canal, id_casa, id_senda,
            id_etapa_procesal, id_sub_etapa, fecha_radicacion,
            id_clasificacion_juridica, id_mes_embudo, anio, mes_meta, llave,
            meta, id_inversionista_intradia, id_saldo_total, fecha_insercion,
            archivo_cargado, titular_cartera, id_pais, id_aliado, id_segmento,
            edad, id_ocupacion, id_producto, id_portafolio, funder
        FROM embudo_mes
    """)

    # Convertimos cada fila en un diccionario
    embudos = []
    for row in cursor.fetchall():
        embudos.append({
            "id_titular": row.id_titular,
            "id_sucursal": row.id_sucursal,
            "id_estado_obligacion": row.id_estado_obligacion,
            "es_fallecido": row.es_fallecido,
            "judicializado": row.judicializado,
            "saldo_capital": row.saldo_capital,
            "saldo_capital_consolidado": row.saldo_capital_consolidado,
            "porcentaje_participacion": row.porcentaje_participacion,
            "id_estado_reporte_cifin": row.id_estado_reporte_cifin,
            "id_estado_reporte_datacredito": row.id_estado_reporte_datacredito,
            "id_originador": row.id_originador,
            "id_inversionista": row.id_inversionista,
            "id_canal": row.id_canal,
            "id_casa": row.id_casa,
            "id_senda": row.id_senda,
            "id_etapa_procesal": row.id_etapa_procesal,
            "id_sub_etapa": row.id_sub_etapa,
            "fecha_radicacion": row.fecha_radicacion,
            "id_clasificacion_juridica": row.id_clasificacion_juridica,
            "id_mes_embudo": row.id_mes_embudo,
            "anio": row.anio,
            "mes_meta": row.mes_meta,
            "llave": row.llave,
            "meta": row.meta,
            "id_inversionista_intradia": row.id_inversionista_intradia,
            "id_saldo_total": row.id_saldo_total,
            "fecha_insercion": row.fecha_insercion,
            "archivo_cargado": row.archivo_cargado,
            "titular_cartera": row.titular_cartera,
            "id_pais": row.id_pais,
            "id_aliado": row.id_aliado,
            "id_segmento": row.id_segmento,
            "edad": row.edad,
            "id_ocupacion": row.id_ocupacion,
            "id_producto": row.id_producto,
            "id_portafolio": row.id_portafolio,
            "funder": row.funder
        })

    # Cerramos cursor y conexión
    cursor.close()
    conn.close()

    return embudos
