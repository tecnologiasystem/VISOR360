import pyodbc
from app.database import get_connection

TASA_USD = 3700  # tasa fija temporal

def obtener_recaudo_por_dia(nombre_campana: str = None,
                              mes: int = None,
                              dia_corte: int = None,
                              year: int = None):
    """
    Obtiene el recaudo total filtrado por día de corte.
    
    Args:
        nombre_campana: Nombre de la campaña (búsqueda parcial con LIKE)
        mes: Mes (1-12)
        dia_corte: Rango de días (1, 10, 20 o None para todo el mes)
        year: Año (default: año actual)
    
    Returns:
        Lista de tuplas (fecha, total_usd)
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            SUM(r.valor_recaudo) / ? AS total_usd
        FROM [marcacion] m
        INNER JOIN [marcacion_titular] mt ON m.telefono_marcado = mt.telefono_marcado
        INNER JOIN [recaudo] r ON mt.id_titular = r.id_titular
        WHERE 1=1
    """

    params = [TASA_USD]

    # FILTRO: campaña
    if nombre_campana:
        sql += " AND mt.nombre_campana LIKE ? "
        params.append(f"%{nombre_campana}%")

    # FILTRO: año
    if year:
        sql += " AND YEAR(r.fecha_recaudo) = ? "
        params.append(year)

    # FILTRO: mes
    if mes:
        sql += " AND MONTH(r.fecha_recaudo) = ? "
        params.append(mes)

    # FILTRO: día de corte (1-10, 10-20, 20-fin de mes)
    if dia_corte == 1:
        sql += " AND DAY(r.fecha_recaudo) BETWEEN 1 AND 9 "
    elif dia_corte == 10:
        sql += " AND DAY(r.fecha_recaudo) BETWEEN 10 AND 19 "
    elif dia_corte == 20:
        sql += " AND DAY(r.fecha_recaudo) BETWEEN 20 AND 31 "

    # No se necesita GROUP BY ni ORDER BY para un solo total

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def obtener_recaudo_por_mes(nombre_campana: str = None,
                             mes: int = None,
                             year: int = None):
    """
    Obtiene el recaudo día por día en USD para un mes específico.
    
    Args:
        nombre_campana: Nombre de la campaña (búsqueda parcial con LIKE)
        mes: Mes (1-12)
        year: Año (default: año actual)
    
    Returns:
        Lista de tuplas (fecha, total_usd)
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            CONVERT(date, r.fecha_recaudo) AS fecha,
            SUM(r.valor_recaudo) / ? AS total_usd
        FROM [marcacion] m
        INNER JOIN [marcacion_titular] mt ON m.telefono_marcado = mt.telefono_marcado
        INNER JOIN [recaudo] r ON mt.id_titular = r.id_titular
        WHERE 1=1
    """

    params = [TASA_USD]

    # FILTRO: campaña
    if nombre_campana:
        sql += " AND mt.nombre_campana LIKE ? "
        params.append(f"%{nombre_campana}%")

    # FILTRO: año
    if year:
        sql += " AND YEAR(r.fecha_recaudo) = ? "
        params.append(year)

    # FILTRO: mes
    if mes:
        sql += " AND MONTH(r.fecha_recaudo) = ? "
        params.append(mes)

    sql += """
        GROUP BY CONVERT(date, r.fecha_recaudo)
        ORDER BY fecha ASC
    """

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def obtener_recaudo_ultimos_4_meses(nombre_campana: str = None, year: int = None):
    """
    Obtiene el recaudo total de los últimos 4 meses (agosto a noviembre) desglosado por mes.
    
    Args:
        nombre_campana: Nombre de la campaña (búsqueda parcial con LIKE)
        year: Año (default: año actual)
    
    Returns:
        Lista de tuplas (mes, total_usd)
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            MONTH(r.fecha_recaudo) AS mes,
            SUM(r.valor_recaudo) / ? AS total_usd
        FROM [marcacion] m
        INNER JOIN [marcacion_titular] mt ON m.telefono_marcado = mt.telefono_marcado
        INNER JOIN [recaudo] r ON mt.id_titular = r.id_titular
        WHERE 1=1
        AND YEAR(r.fecha_recaudo) = ?
        AND MONTH(r.fecha_recaudo) >= 8
        AND MONTH(r.fecha_recaudo) <= 11
    """

    params = [TASA_USD, year]

    # FILTRO: campaña
    if nombre_campana:
        sql += " AND mt.nombre_campana LIKE ? "
        params.append(f"%{nombre_campana}%")

    sql += """
        GROUP BY MONTH(r.fecha_recaudo)
        ORDER BY MONTH(r.fecha_recaudo) ASC
    """

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows
