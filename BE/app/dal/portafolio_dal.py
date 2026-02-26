"""
DAL para la vista vw_recaudos_portafolio.
Obtiene datos de recaudo de campañas pequeñas de Colombia desde la BD.

La vista tiene las siguientes columnas:
- id_pais
- nombre_pais_portafolio (ej: "SYSTEMGROUP COLOMBIA", "SYSTEMGROUP CREDIVALORES NPL", etc.)
- mes
- dia
- valor_pago_total

Campañas disponibles en la BD:
NPL:
  - SYSTEMGROUP CREDIVALORES NPL
ACC:
  - SYSTEMGROUP ACCION FIDUCIARIA- DENTIX
  - SYSTEMGROUP ADAMANTINE - COLPATRIA NPL
  - SYSTEMGROUP JCAP
  - SYSTEMGROUP PRA GROUP
  - SYSTEMGROUP COLOMBIA (total general ACC)
"""

from app.database import get_connection_portafolio, get_campana_bd_name, CAMPANAS_PEQUENAS_BD_MAPPING
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def obtener_recaudo_campana_portafolio(
    nombre_campana_bd: str, 
    mes: int, 
    anio: int, 
    hasta_dia: int = None
) -> Dict:
    """
    Obtiene el recaudo total de una campaña desde vw_recaudos_portafolio.
    
    Args:
        nombre_campana_bd: Nombre exacto en la columna nombre_pais_portafolio
        mes: Mes (1-12)
        anio: Año
        hasta_dia: Día límite (opcional, para "hasta hoy")
    
    Returns:
        Dict con total y cantidad
    """
    try:
        conn = get_connection_portafolio()
        cursor = conn.cursor()
        
        # Construir query base - usando vw_recaudos_portafoliov2
        query = """
            SELECT 
                ISNULL(SUM(valor_pago_total), 0) as total,
                COUNT(*) as cantidad
            FROM vw_recaudos_portafoliov2
            WHERE nombre_pais_portafolio = ?
            AND mes = ?
            AND anio = ?
        """
        params = [nombre_campana_bd, mes, anio]
        
        # Agregar filtro de día si se especifica
        if hasta_dia is not None:
            query += " AND dia <= ?"
            params.append(hasta_dia)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "total": float(row[0]) if row and row[0] else 0.0,
            "cantidad": int(row[1]) if row and row[1] else 0
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo recaudo de portafolio: {e}")
        return {"total": 0.0, "cantidad": 0}


def obtener_recaudo_diario_portafolio(
    nombre_campana_bd: str, 
    mes: int, 
    anio: int
) -> List[Dict]:
    """
    Obtiene el recaudo agrupado por día desde vw_recaudos_portafolio.
    
    Returns:
        Lista de dicts con fecha, total, cantidad por día
    """
    try:
        conn = get_connection_portafolio()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                dia,
                ISNULL(SUM(valor_pago_total), 0) as total_dia
            FROM vw_recaudos_portafoliov2
            WHERE nombre_pais_portafolio = ?
            AND mes = ?
            AND anio = ?
            GROUP BY dia
            ORDER BY dia
        """
        
        cursor.execute(query, (nombre_campana_bd, mes, anio))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        resultado = []
        for row in rows:
            # Construir fecha ISO (asumiendo año actual si no está en la vista)
            dia = int(row[0]) if row[0] else 1
            fecha_iso = f"{anio}-{mes:02d}-{dia:02d}"
            resultado.append({
                "fecha": fecha_iso,
                "dia": dia,
                "total": float(row[1]) if row[1] else 0.0,
                "cantidad": 1  # La vista ya agrupa, así que es 1 registro por día
            })
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error obteniendo recaudo diario de portafolio: {e}")
        return []


from app.utils.dias_habiles import obtener_dias_habiles_mes, obtener_dia_habil_actual


def obtener_recaudo_diario_teseo_peru(mes: int, anio: int) -> List[Dict]:
    """
    Obtiene la serie diaria desde la vista `vw_recaudo_teseo_peru`.
    La vista tiene columnas: campana, anio_mes, dia_habil, nombre_inversionista, nombre_portafolio, valor_recaudo
    
    Devuelve lista de dicts con claves: `fecha` (ISO), `total`, `cantidad`.
    """
    try:
        conn = get_connection_portafolio()
        cursor = conn.cursor()
        
        # Construir anio_mes formato 'YYYY-MM'
        anio_mes_str = f"{anio}-{mes:02d}"
        
        # Consulta usando la estructura correcta de la vista: anio_mes y dia_habil
        query = """
            SELECT dia_habil, ISNULL(SUM(valor_recaudo), 0) as total, COUNT(*) as cantidad
            FROM vw_recaudo_teseo_peru
            WHERE anio_mes = ?
            GROUP BY dia_habil
            ORDER BY dia_habil
        """
        cursor.execute(query, (anio_mes_str,))
        rows = cursor.fetchall()
        
        resultado = []
        for row in rows:
            dia_habil = int(row[0]) if row[0] is not None else 1
            # dia_habil es el número del día hábil, necesitamos la fecha real
            dias_habiles = obtener_dias_habiles_mes(anio, mes)
            if dia_habil <= len(dias_habiles):
                fecha_iso = dias_habiles[dia_habil - 1]["fecha"]  # dia_habil es 1-based
            else:
                # Si el día hábil excede los días calculados, construir fecha aproximada
                fecha_iso = f"{anio}-{mes:02d}-{dia_habil:02d}"
            
            resultado.append({
                "fecha": fecha_iso,
                "dia_habil": dia_habil,
                "total": float(row[1]) if row[1] is not None else 0.0,
                "cantidad": int(row[2]) if row[2] is not None else 0,
                "distribuido": False
            })
        
        # Si hay filas, rellenar días hábiles faltantes con 0
        if resultado:
            mapa = {r["dia_habil"]: r["total"] for r in resultado}
            dias_habiles = obtener_dias_habiles_mes(anio, mes)
            total_dias_habiles = len(dias_habiles)
            dias_transcurridos = obtener_dia_habil_actual(anio, mes)
            if dias_transcurridos <= 0:
                dias_transcurridos = total_dias_habiles
            
            llenado = []
            for i in range(min(dias_transcurridos, total_dias_habiles)):
                dia_habil_num = i + 1  # 1-based
                fecha_iso = dias_habiles[i]["fecha"]
                total_val = float(mapa.get(dia_habil_num, 0.0))
                llenado.append({
                    "fecha": fecha_iso,
                    "total": total_val,
                    "cantidad": 0,
                    "distribuido": False,
                    "fuente": "diaria_filled"
                })
            cursor.close()
            conn.close()
            return llenado
        
        # Si la serie está vacía, distribuir el total mensual como fallback
        dias_habiles = obtener_dias_habiles_mes(anio, mes)
        total_dias_habiles = len(dias_habiles)
        if total_dias_habiles > 0:
            try:
                cursor2 = conn.cursor()
                query_sum = """
                    SELECT ISNULL(SUM(valor_recaudo), 0) FROM vw_recaudo_teseo_peru
                    WHERE anio_mes = ?
                """
                cursor2.execute(query_sum, (anio_mes_str,))
                row_sum = cursor2.fetchone()
                cursor2.close()
                total_mes = float(row_sum[0]) if row_sum and row_sum[0] is not None else 0.0
                dias_transcurridos = obtener_dia_habil_actual(anio, mes)
                if dias_transcurridos <= 0:
                    dias_transcurridos = total_dias_habiles
                per_day = total_mes / dias_transcurridos if dias_transcurridos > 0 else 0.0
                distribuida = []
                for i in range(min(dias_transcurridos, total_dias_habiles)):
                    fecha_iso = dias_habiles[i]["fecha"]
                    distribuida.append({
                        "fecha": fecha_iso,
                        "total": round(per_day, 2),
                        "cantidad": 0,
                        "distribuido": True,
                        "fuente": "distribuida"
                    })
                cursor.close()
                conn.close()
                return distribuida
            except Exception:
                cursor.close()
                conn.close()
                return []
        
        cursor.close()
        conn.close()
        return []

    except Exception as e:
        logger.error(f"Error obteniendo recaudo diario Teseo Peru: {e}")
        return []


def obtener_campanas_disponibles_portafolio(mes: int = None) -> List[str]:
    """
    Obtiene la lista de nombres de campaña disponibles en la vista.
    
    Args:
        mes: Filtrar por mes específico (opcional)
    
    Returns:
        Lista de nombres de campaña únicos
    """
    try:
        conn = get_connection_portafolio()
        cursor = conn.cursor()
        
        if mes:
            query = """
                SELECT DISTINCT nombre_pais_portafolio
                FROM vw_recaudos_portafoliov2
                WHERE mes = ?
                ORDER BY nombre_pais_portafolio
            """
            cursor.execute(query, (mes,))
        else:
            query = """
                SELECT DISTINCT nombre_pais_portafolio
                FROM vw_recaudos_portafoliov2
                ORDER BY nombre_pais_portafolio
            """
            cursor.execute(query)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [row[0] for row in rows if row[0]]
        
    except Exception as e:
        logger.error(f"Error obteniendo campañas disponibles: {e}")
        return []


def obtener_total_pais_portafolio(
    pais: str,
    mes: int, 
    anio: int,
    hasta_dia: int = None
) -> Dict:
    """
    Obtiene el total de recaudo para un país (suma de todas sus campañas pequeñas).
    
    Args:
        pais: "NPL", "ACC", etc.
        mes: Mes (1-12)
        anio: Año
        hasta_dia: Día límite opcional
    
    Returns:
        Dict con total y cantidad
    """
    pais_upper = pais.upper().strip()
    total = 0.0
    cantidad = 0

    # Manejo especial para Perú: intentar sumar directamente desde la vista Teseo
    if "PER" in pais_upper:
        try:
            conn = get_connection_portafolio()
            cursor = conn.cursor()
            # Construir anio_mes formato 'YYYY-MM'
            anio_mes_str = f"{anio}-{mes:02d}"
            query = """
                SELECT ISNULL(SUM(valor_recaudo), 0) as total, COUNT(*) as cantidad
                FROM vw_recaudo_teseo_peru
                WHERE anio_mes = ?
            """
            cursor.execute(query, (anio_mes_str,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return {
                "total": float(row[0]) if row and row[0] else 0.0,
                "cantidad": int(row[1]) if row and row[1] else 0,
            }
        except Exception:
            # caemos al flujo normal (buscar por campañas) si falla
            pass
    
    # Determinar qué campañas sumar según el país
    campanas_bd = []
    
    if "NPL" in pais_upper and "COL" in pais_upper:
        # NPL Colombia - sumar las campañas NPL que tienen datos en BD
        campanas_bd = ["SYSTEMGROUP CREDIVALORES NPL"]
    elif "ACC" in pais_upper or "SYSTEMGROUP" in pais_upper:
        # ACC - todas las campañas pequeñas de ACC
        # Podemos usar SYSTEMGROUP COLOMBIA que es el total, o sumar individualmente
        campanas_bd = ["SYSTEMGROUP COLOMBIA"]  # Este ya es el total
    
    # Si no hay campañas específicas, intentar buscar directamente
    if not campanas_bd:
        # Buscar campañas que contengan el nombre del país
        todas_campanas = obtener_campanas_disponibles_portafolio(mes)
        campanas_bd = [c for c in todas_campanas if pais_upper in c.upper()]
    
    # Sumar recaudo de todas las campañas encontradas
    for campana in campanas_bd:
        result = obtener_recaudo_campana_portafolio(campana, mes, anio, hasta_dia)
        total += result["total"]
        cantidad += result["cantidad"]
    
    return {"total": total, "cantidad": cantidad}


def obtener_subcampanas_pais_portafolio(
    pais: str,
    mes: int,
    anio: int
) -> List[Dict]:
    """
    Obtiene el desglose por subcampañas de un país.
    
    SOLO retorna campañas que tienen datos en BD.
    Para países sin datos en BD (NPL PER, NPL CHILE), retorna None
    para indicar que debe usarse Excel completo.
    
    Args:
        pais: "NPL", "ACC", "NPL COL", etc.
        mes: Mes (1-12)
        anio: Año
    
    Returns:
        Lista de dicts con nombre_campana, nombre_bd, total, cantidad, fuente
        None si el país no tiene datos en BD (usar Excel)
    """
    pais_upper = pais.upper().strip()
    
    # Manejo especial para Perú: intentar obtener datos desde la vista
    # `vw_recaudo_teseo_peru`. Si la vista no existe o la consulta falla,
    # devolvemos None para que el caller use el fallback por Excel.
    if "PER" in pais_upper:
        try:
            conn = get_connection_portafolio()
            cursor = conn.cursor()

            # Consulta asumiendo columnas típicas en la vista Teseo.
            # La vista debe exponer el inversionista/subcampaña y el valor del pago.
            # Consulta ajustada al SQL del usuario: usar anio_mes y valor_recaudo (según screenshot)
            query = """
                SELECT
                    ISNULL(nombre_inversionista, '') AS nombre_inversionista,
                    ISNULL(SUM(valor_recaudo), 0) AS total_bd,
                    COUNT(*) AS cantidad_bd
                FROM vw_recaudo_teseo_peru
                WHERE anio_mes = ?
                GROUP BY nombre_inversionista
                ORDER BY nombre_inversionista
            """
            
            # Construir anio_mes formato 'YYYY-MM'
            anio_mes_str = f"{anio}-{mes:02d}"
            cursor.execute(query, (anio_mes_str,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            resultado = []
            for row in rows:
                nombre = row[0] or ""
                total = float(row[1]) if row[1] is not None else 0.0
                cantidad = int(row[2]) if row[2] is not None else 0
                resultado.append({
                    "nombre_campana": nombre,
                    "nombre_bd": None,
                    "total_bd": total,
                    "cantidad_bd": cantidad,
                    "tiene_datos_bd": True,
                })

            return resultado
        except Exception:
            # Si falla, indicar que no hay datos en BD para usar Excel
            return None

    # Manejo especial para Chile: consultar de vw_recaudos_portafoliov2
    if "CHILE" in pais_upper:
        try:
            conn = get_connection_portafolio()
            cursor = conn.cursor()
            query = """
                SELECT ISNULL(SUM(valor_pago_total), 0) as total_bd
                FROM vw_recaudos_portafoliov2
                WHERE nombre_pais_portafolio = 'SYSTEMGROUP CHILE'
                AND mes = ?
                AND anio = ?
            """
            cursor.execute(query, (mes, anio))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            total = float(row[0]) if row and row[0] else 0.0
            
            return [{
                "nombre_campana": "IFC",
                "nombre_bd": "SYSTEMGROUP CHILE",
                "total_bd": total,
                "cantidad_bd": 1 if total > 0 else 0,
                "tiene_datos_bd": total > 0,
            }]
        except Exception:
            return None
    
    # Obtener mapeo de campañas para este país
    campanas_mapping = None
    
    # Buscar en el mapeo - intentar coincidencia exacta o parcial
    for pais_key in CAMPANAS_PEQUENAS_BD_MAPPING:
        pais_key_upper = pais_key.upper()
        # Coincidencia exacta
        if pais_key_upper == pais_upper:
            campanas_mapping = CAMPANAS_PEQUENAS_BD_MAPPING[pais_key]
            break
        # Coincidencia parcial solo si el key está contenido en el pais buscado
        # y es más específico (tiene más de 3 caracteres)
        if pais_key_upper in pais_upper and "NPL" in pais_key_upper:
            campanas_mapping = CAMPANAS_PEQUENAS_BD_MAPPING[pais_key]
            break
    
    if not campanas_mapping:
        return None  # País no configurado, usar Excel
    
    resultado = []
    
    # Para cada campaña pequeña configurada
    for campana_fe, campana_bd in campanas_mapping.items():
        recaudo_bd = {"total": 0.0, "cantidad": 0}
        tiene_datos_bd = False
        
        # Intentar obtener datos de BD si hay mapeo
        if campana_bd is not None:
            try:
                recaudo_bd = obtener_recaudo_campana_portafolio(campana_bd, mes, anio)
                if recaudo_bd["total"] > 0 or recaudo_bd["cantidad"] > 0:
                    tiene_datos_bd = True
            except Exception as e:
                logger.warning(f"Error obteniendo {campana_bd} de BD: {e}")
        
        resultado.append({
            "nombre_campana": campana_fe,
            "nombre_bd": campana_bd,
            "total_bd": recaudo_bd["total"] if tiene_datos_bd else 0.0,
            "cantidad_bd": recaudo_bd["cantidad"] if tiene_datos_bd else 0,
            "tiene_datos_bd": tiene_datos_bd,
        })
    
    return resultado


def verificar_conexion_portafolio() -> bool:
    """
    Verifica que la conexión a la BD de portafolio funcione.
    
    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        conn = get_connection_portafolio()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 1 FROM vw_recaudos_portafoliov2")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error verificando conexión portafolio: {e}")
        return False


def obtener_resumen_mensual_portafolio(mes: int, anio: int) -> List[Dict]:
    """
    Obtiene un resumen de recaudo mensual por campaña.
    
    Returns:
        Lista de dicts con nombre_campana, total_mes
    """
    try:
        conn = get_connection_portafolio()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                nombre_pais_portafolio,
                ISNULL(SUM(valor_pago_total), 0) as total_mes
            FROM vw_recaudos_portafoliov2
            WHERE mes = ?
            AND anio = ?
            GROUP BY nombre_pais_portafolio
            ORDER BY total_mes DESC
        """
        
        cursor.execute(query, (mes, anio))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                "nombre_campana": row[0],
                "total_mes": float(row[1]) if row[1] else 0.0,
                "mes": mes,
                "anio": anio
            }
            for row in rows if row[0]
        ]
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen mensual: {e}")
        return []


def obtener_recaudo_tanque_sin_identificar(
    nombre_campana_bd: str,
    mes: int,
    anio: int,
    hasta_dia: int = None
) -> Dict:
    """
    Obtiene el recaudo sin identificar (tanque) de una campaña desde vw_tanque_sin_identificar.
    
    Args:
        nombre_campana_bd: Nombre exacto en la columna nombre_pais_portafolio
        mes: Mes (1-12)
        anio: Año
        hasta_dia: Día límite (opcional, para "hasta hoy")
    
    Returns:
        Dict con total, cantidad de recaudos sin identificar
    """
    try:
        conn = get_connection_portafolio()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                ISNULL(SUM(valor_recaudo_no_identificado), 0) as total,
                ISNULL(SUM(cantidad_recaudos_sin_identificar), 0) as cantidad
            FROM vw_tanque_sin_identificar
            WHERE nombre_pais_portafolio = ?
            AND mes = ?
            AND anio = ?
        """
        params = [nombre_campana_bd, mes, anio]
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "total": float(row[0]) if row and row[0] else 0.0,
            "cantidad": int(row[1]) if row and row[1] else 0
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo recaudo tanque sin identificar: {e}")
        return {"total": 0.0, "cantidad": 0}


def obtener_recaudo_tanque_pais(
    pais: str,
    mes: int,
    anio: int,
    hasta_dia: int = None
) -> Dict:
    """
    Obtiene el recaudo sin identificar (tanque) total de un país.
    
    Args:
        pais: "NPL", "ACC", "NPL COL", "CHILE", etc.
        mes: Mes (1-12)
        anio: Año
        hasta_dia: Día límite opcional
    
    Returns:
        Dict con total y cantidad de recaudos sin identificar
    """
    pais_upper = pais.upper().strip()
    total = 0.0
    cantidad = 0
    
    # Determinar qué campañas sumar según el país
    campanas_bd = []
    
    if "NPL" in pais_upper and "COL" in pais_upper:
        # NPL Colombia
        campanas_bd = ["SYSTEMGROUP CREDIVALORES NPL"]
    elif "ACC" in pais_upper or "SYSTEMGROUP" in pais_upper:
        # ACC - usar el total general
        campanas_bd = ["SYSTEMGROUP COLOMBIA"]
    elif "CHILE" in pais_upper:
        campanas_bd = ["SYSTEMGROUP CHILE"]
    
    # Si no hay campañas específicas, intentar buscar directamente
    if not campanas_bd:
        # Buscar campañas que contengan el nombre del país
        try:
            conn = get_connection_portafolio()
            cursor = conn.cursor()
            query = """
                SELECT DISTINCT nombre_pais_portafolio
                FROM vw_tanque_sin_identificar
                WHERE mes = ? AND anio = ?
            """
            cursor.execute(query, (mes, anio))
            todas_campanas = [row[0] for row in cursor.fetchall() if row[0]]
            cursor.close()
            conn.close()
            campanas_bd = [c for c in todas_campanas if pais_upper in c.upper()]
        except Exception:
            pass
    
    # Sumar recaudo de todas las campañas encontradas
    for campana in campanas_bd:
        result = obtener_recaudo_tanque_sin_identificar(campana, mes, anio, hasta_dia)
        total += result["total"]
        cantidad += result["cantidad"]
    
    return {"total": total, "cantidad": cantidad}
