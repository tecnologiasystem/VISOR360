"""
DAL para las tablas de Planta Activa (Colombia, Perú, Panamá).
Obtiene estadísticas de empleados activos para el Radar de Talento Humano.

Tablas:
- PlantaActivaCol: Empleados de Colombia (salario_mensual, genero, edad)
- PlantaActivaPer: Empleados de Perú (salario_mensual, genero, edad)
- PlantaActivaPan: Empleados de Panamá (salario_regular, genero, edad)
"""

from app.database import get_connection1
from typing import Dict
import logging

logger = logging.getLogger(__name__)


# ========== COLOMBIA ==========

def obtener_estadisticas_colombia(mes: int = None, anio: int = None) -> Dict:
    """
    Obtiene estadísticas de empleados de Colombia.
    Filtra por fecha_corte si se especifica mes/año.
    
    Consultas:
    1. COUNT(*) as Personal_Activo from PlantaActivaCol WHERE MONTH(fecha_corte)=? AND YEAR(fecha_corte)=?
    2. SUM(salario_mensual) as Costo_Recurso_Humano from PlantaActivaCol WHERE...
    3. genero, COUNT(genero) as Genero from PlantaActivaCol WHERE... group by genero
    4. AVG(CAST(edad AS decimal(10, 2))) AS Edad_Prom from PlantaActivaCol WHERE...
    """
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        # Construir WHERE clause
        # Formato fecha_corte: YYYY-MM-DD (el mes está en la segunda parte)
        where_clause = ""
        params = []
        if mes and anio:
            where_clause = " WHERE MONTH(fecha_corte) = ? AND YEAR(fecha_corte) = ?"
            params = [mes, anio]
        
        # 1. Personal Activo
        cursor.execute(f"SELECT COUNT(*) as Personal_Activo FROM PlantaActivaCol{where_clause}", params)
        personal_activo = cursor.fetchone()[0]
        
        # 2. Costo Recurso Humano
        cursor.execute(f"SELECT SUM(salario_mensual) as Costo_Recurso_Humano FROM PlantaActivaCol{where_clause}", params)
        costo_rh = cursor.fetchone()[0] or 0
        
        # 3. Distribución por género
        cursor.execute(f"SELECT genero, COUNT(genero) as Genero FROM PlantaActivaCol{where_clause} GROUP BY genero", params)
        generos_raw = cursor.fetchall()
        generos = {}
        for row in generos_raw:
            genero = row[0] if row[0] else "Sin dato"
            cantidad = row[1]
            generos[genero] = cantidad
        
        # 4. Edad promedio
        cursor.execute(f"SELECT AVG(CAST(edad AS decimal(10, 2))) AS Edad_Prom FROM PlantaActivaCol{where_clause}", params)
        edad_prom = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return {
            "pais": "COLOMBIA",
            "personal_activo": personal_activo,
            "costo_recurso_humano": float(costo_rh),
            "generos": generos,
            "edad_promedio": float(edad_prom)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas Colombia: {e}")
        return {
            "pais": "COLOMBIA",
            "personal_activo": 0,
            "costo_recurso_humano": 0.0,
            "generos": {},
            "edad_promedio": 0.0
        }


# ========== PERÚ ==========

def obtener_estadisticas_peru(mes: int = None, anio: int = None) -> Dict:
    """
    Obtiene estadísticas de empleados de Perú.
    Filtra por fecha_corte si se especifica mes/año.
    
    Consultas:
    1. COUNT(*) as Personal_Activo from PlantaActivaPer WHERE MONTH(fecha_corte)=? AND YEAR(fecha_corte)=?
    2. SUM(salario_mensual) as Costo_Recurso_Humano from PlantaActivaPer WHERE...
    3. genero, COUNT(genero) as Genero from PlantaActivaPer WHERE... group by genero
    4. AVG(CAST(edad AS decimal(10, 2))) AS Edad_Prom from PlantaActivaPer WHERE...
    """
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        # Construir WHERE clause
        # Formato fecha_corte: YYYY-MM-DD (el mes está en la segunda parte)
        where_clause = ""
        params = []
        if mes and anio:
            where_clause = " WHERE MONTH(fecha_corte) = ? AND YEAR(fecha_corte) = ?"
            params = [mes, anio]
        
        # 1. Personal Activo
        cursor.execute(f"SELECT COUNT(*) as Personal_Activo FROM PlantaActivaPer{where_clause}", params)
        personal_activo = cursor.fetchone()[0]
        
        # 2. Costo Recurso Humano
        cursor.execute(f"SELECT SUM(salario_mensual) as Costo_Recurso_Humano FROM PlantaActivaPer{where_clause}", params)
        costo_rh = cursor.fetchone()[0] or 0
        
        # 3. Distribución por género
        cursor.execute(f"SELECT genero, COUNT(genero) as Genero FROM PlantaActivaPer{where_clause} GROUP BY genero", params)
        generos_raw = cursor.fetchall()
        generos = {}
        for row in generos_raw:
            genero = row[0] if row[0] else "Sin dato"
            cantidad = row[1]
            generos[genero] = cantidad
        
        # 4. Edad promedio
        cursor.execute(f"SELECT AVG(CAST(edad AS decimal(10, 2))) AS Edad_Prom FROM PlantaActivaPer{where_clause}", params)
        edad_prom = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return {
            "pais": "PERU",
            "personal_activo": personal_activo,
            "costo_recurso_humano": float(costo_rh),
            "generos": generos,
            "edad_promedio": float(edad_prom)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas Perú: {e}")
        return {
            "pais": "PERU",
            "personal_activo": 0,
            "costo_recurso_humano": 0.0,
            "generos": {},
            "edad_promedio": 0.0
        }


# ========== PANAMÁ ==========

def obtener_estadisticas_panama(mes: int = None, anio: int = None) -> Dict:
    """
    Obtiene estadísticas de empleados de Panamá.
    Filtra por fecha_corte si se especifica mes/año.
    
    Consultas:
    1. COUNT(*) as Personal_Activo from PlantaActivaPan WHERE MONTH(fecha_corte)=? AND YEAR(fecha_corte)=?
    2. SUM(salario_regular) as Costo_Recurso_Humano from PlantaActivaPan WHERE...
    3. genero, COUNT(genero) as Genero from PlantaActivaPan WHERE... group by genero
    4. AVG(CAST(edad AS decimal(10, 2))) AS Edad_Prom from PlantaActivaPan WHERE...
    
    NOTA: Panamá usa 'salario_regular' en lugar de 'salario_mensual'
    """
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        # Construir WHERE clause
        # Formato fecha_corte: YYYY-MM-DD (el mes está en la segunda parte)
        where_clause = ""
        params = []
        if mes and anio:
            where_clause = " WHERE MONTH(fecha_corte) = ? AND YEAR(fecha_corte) = ?"
            params = [mes, anio]
        
        # 1. Personal Activo
        cursor.execute(f"SELECT COUNT(*) as Personal_Activo FROM PlantaActivaPan{where_clause}", params)
        personal_activo = cursor.fetchone()[0]
        
        # 2. Costo Recurso Humano (salario_regular en lugar de salario_mensual)
        cursor.execute(f"SELECT SUM(salario_regular) as Costo_Recurso_Humano FROM PlantaActivaPan{where_clause}", params)
        costo_rh = cursor.fetchone()[0] or 0
        
        # 3. Distribución por género
        cursor.execute(f"SELECT genero, COUNT(genero) as Genero FROM PlantaActivaPan{where_clause} GROUP BY genero", params)
        generos_raw = cursor.fetchall()
        generos = {}
        for row in generos_raw:
            genero = row[0] if row[0] else "Sin dato"
            cantidad = row[1]
            generos[genero] = cantidad
        
        # 4. Edad promedio
        cursor.execute(f"SELECT AVG(CAST(edad AS decimal(10, 2))) AS Edad_Prom FROM PlantaActivaPan{where_clause}", params)
        edad_prom = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return {
            "pais": "PANAMA",
            "personal_activo": personal_activo,
            "costo_recurso_humano": float(costo_rh),
            "generos": generos,
            "edad_promedio": float(edad_prom)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas Panamá: {e}")
        return {
            "pais": "PANAMA",
            "personal_activo": 0,
            "costo_recurso_humano": 0.0,
            "generos": {},
            "edad_promedio": 0.0
        }


# ========== AGREGADORES ==========

def obtener_estadisticas_todos_paises(mes: int = None, anio: int = None) -> Dict:
    """
    Obtiene estadísticas de todos los países combinadas.
    Filtra por fecha_corte si se especifica mes/año.
    """
    col = obtener_estadisticas_colombia(mes, anio)
    per = obtener_estadisticas_peru(mes, anio)
    pan = obtener_estadisticas_panama(mes, anio)
    
    # Combinar géneros de los 3 países
    generos_total = {}
    for generos_dict in [col["generos"], per["generos"], pan["generos"]]:
        for genero, cantidad in generos_dict.items():
            if genero not in generos_total:
                generos_total[genero] = 0
            generos_total[genero] += cantidad
    
    # Calcular edad promedio ponderada
    total_empleados = col["personal_activo"] + per["personal_activo"] + pan["personal_activo"]
    if total_empleados > 0:
        edad_prom_total = (
            (col["edad_promedio"] * col["personal_activo"]) +
            (per["edad_promedio"] * per["personal_activo"]) +
            (pan["edad_promedio"] * pan["personal_activo"])
        ) / total_empleados
    else:
        edad_prom_total = 0
    
    return {
        "pais": "TODOS",
        "personal_activo": total_empleados,
        "costo_recurso_humano": col["costo_recurso_humano"] + per["costo_recurso_humano"] + pan["costo_recurso_humano"],
        "generos": generos_total,
        "edad_promedio": round(edad_prom_total, 2),
        "detalle_paises": {
            "colombia": col,
            "peru": per,
            "panama": pan
        }
    }


def obtener_estadisticas_por_pais(pais: str, mes: int = None, anio: int = None) -> Dict:
    """
    Obtiene estadísticas de un país específico.
    Filtra por fecha_corte si se especifica mes/año.
    
    Args:
        pais: "COLOMBIA", "PERU", "PANAMA" o "TODOS"
        mes: Mes de corte (1-12)
        anio: Año de corte
    """
    pais_upper = pais.upper().strip()
    
    if pais_upper in ["COLOMBIA", "COL"]:
        return obtener_estadisticas_colombia(mes, anio)
    elif pais_upper in ["PERU", "PER"]:
        return obtener_estadisticas_peru(mes, anio)
    elif pais_upper in ["PANAMA", "PAN"]:
        return obtener_estadisticas_panama(mes, anio)
    elif pais_upper == "TODOS":
        return obtener_estadisticas_todos_paises(mes, anio)
    else:
        logger.warning(f"País no reconocido: {pais}. Devolviendo todos los países.")
        return obtener_estadisticas_todos_paises(mes, anio)


# ========== DATOS DETALLADOS ==========

def obtener_detalle_unidades(pais: str = None, mes: int = None, anio: int = None) -> list:
    """
    Obtiene distribución por unidad de negocio.
    """
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        where_clause = ""
        params = []
        if mes and anio:
            where_clause = " WHERE MONTH(fecha_corte) = ? AND YEAR(fecha_corte) = ?"
            params = [mes, anio]
        
        resultado = []
        
        # Colombia
        if pais is None or pais.upper() in ["COLOMBIA", "COL", "TODOS"]:
            cursor.execute(f"SELECT unidad_negocio, COUNT(*) as cantidad FROM PlantaActivaCol{where_clause} GROUP BY unidad_negocio ORDER BY cantidad DESC", params)
            for row in cursor.fetchall():
                if row[0]:
                    resultado.append({"unidad": row[0], "cantidad": row[1], "pais": "COL"})
        
        # Perú
        if pais is None or pais.upper() in ["PERU", "PER", "TODOS"]:
            cursor.execute(f"SELECT unidad_negocio, COUNT(*) as cantidad FROM PlantaActivaPer{where_clause} GROUP BY unidad_negocio ORDER BY cantidad DESC", params)
            for row in cursor.fetchall():
                if row[0]:
                    resultado.append({"unidad": row[0], "cantidad": row[1], "pais": "PER"})
        
        cursor.close()
        conn.close()
        
        return resultado[:10]  # Top 10
        
    except Exception as e:
        logger.error(f"Error obteniendo detalle unidades: {e}")
        return []


def obtener_detalle_contratos(pais: str = None, mes: int = None, anio: int = None) -> list:
    """
    Obtiene distribución por tipo de contrato.
    """
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        where_clause = ""
        params = []
        if mes and anio:
            where_clause = " WHERE MONTH(fecha_corte) = ? AND YEAR(fecha_corte) = ?"
            params = [mes, anio]
        
        contratos = {}
        
        # Colombia
        if pais is None or pais.upper() in ["COLOMBIA", "COL", "TODOS"]:
            cursor.execute(f"SELECT contrato, COUNT(*) as cantidad FROM PlantaActivaCol{where_clause} GROUP BY contrato", params)
            for row in cursor.fetchall():
                tipo = row[0] or "Sin dato"
                contratos[tipo] = contratos.get(tipo, 0) + row[1]
        
        # Perú
        if pais is None or pais.upper() in ["PERU", "PER", "TODOS"]:
            cursor.execute(f"SELECT contrato, COUNT(*) as cantidad FROM PlantaActivaPer{where_clause} GROUP BY contrato", params)
            for row in cursor.fetchall():
                tipo = row[0] or "Sin dato"
                contratos[tipo] = contratos.get(tipo, 0) + row[1]
        
        cursor.close()
        conn.close()
        
        resultado = [{"tipo": k, "cantidad": v} for k, v in sorted(contratos.items(), key=lambda x: x[1], reverse=True)]
        return resultado
        
    except Exception as e:
        logger.error(f"Error obteniendo detalle contratos: {e}")
        return []


def obtener_detalle_departamentos(pais: str = None, mes: int = None, anio: int = None) -> list:
    """
    Obtiene distribución por departamento.
    """
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        where_clause = ""
        params = []
        if mes and anio:
            where_clause = " WHERE MONTH(fecha_corte) = ? AND YEAR(fecha_corte) = ?"
            params = [mes, anio]
        
        departamentos = {}
        
        # Colombia
        if pais is None or pais.upper() in ["COLOMBIA", "COL", "TODOS"]:
            cursor.execute(f"SELECT departamento, COUNT(*) as cantidad, SUM(salario_mensual) as salario FROM PlantaActivaCol{where_clause} GROUP BY departamento", params)
            for row in cursor.fetchall():
                depto = row[0] or "Sin dato"
                if depto not in departamentos:
                    departamentos[depto] = {"cantidad": 0, "salario": 0}
                departamentos[depto]["cantidad"] += row[1]
                departamentos[depto]["salario"] += row[2] or 0
        
        # Perú
        if pais is None or pais.upper() in ["PERU", "PER", "TODOS"]:
            cursor.execute(f"SELECT departamento, COUNT(*) as cantidad, SUM(salario_mensual) as salario FROM PlantaActivaPer{where_clause} GROUP BY departamento", params)
            for row in cursor.fetchall():
                depto = row[0] or "Sin dato"
                if depto not in departamentos:
                    departamentos[depto] = {"cantidad": 0, "salario": 0}
                departamentos[depto]["cantidad"] += row[1]
                departamentos[depto]["salario"] += row[2] or 0
        
        # Panamá
        if pais is None or pais.upper() in ["PANAMA", "PAN", "TODOS"]:
            cursor.execute(f"SELECT compania, COUNT(*) as cantidad, SUM(salario_regular) as salario FROM PlantaActivaPan{where_clause} GROUP BY compania", params)
            for row in cursor.fetchall():
                depto = row[0] or "Sin dato"
                if depto not in departamentos:
                    departamentos[depto] = {"cantidad": 0, "salario": 0}
                departamentos[depto]["cantidad"] += row[1]
                departamentos[depto]["salario"] += row[2] or 0
        
        cursor.close()
        conn.close()
        
        resultado = [{"departamento": k, "cantidad": v["cantidad"], "salario": v["salario"]} 
                     for k, v in sorted(departamentos.items(), key=lambda x: x[1]["cantidad"], reverse=True)]
        return resultado[:10]  # Top 10
        
    except Exception as e:
        logger.error(f"Error obteniendo detalle departamentos: {e}")
        return []


def obtener_detalle_cargos(pais: str = None, mes: int = None, anio: int = None) -> list:
    """
    Obtiene distribución por cargo.
    SELECT cargo, COUNT(cargo) as total FROM PlantaActivaCol GROUP BY cargo
    """
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        where_clause = ""
        params = []
        if mes and anio:
            where_clause = " WHERE MONTH(fecha_corte) = ? AND YEAR(fecha_corte) = ?"
            params = [mes, anio]
        
        cargos = {}
        
        # Colombia
        if pais is None or pais.upper() in ["COLOMBIA", "COL", "TODOS"]:
            cursor.execute(f"SELECT cargo, COUNT(cargo) as total FROM PlantaActivaCol{where_clause} GROUP BY cargo", params)
            for row in cursor.fetchall():
                cargo_name = row[0] or "Sin dato"
                cargos[cargo_name] = cargos.get(cargo_name, 0) + row[1]
        
        # Perú
        if pais is None or pais.upper() in ["PERU", "PER", "TODOS"]:
            cursor.execute(f"SELECT cargo, COUNT(cargo) as total FROM PlantaActivaPer{where_clause} GROUP BY cargo", params)
            for row in cursor.fetchall():
                cargo_name = row[0] or "Sin dato"
                cargos[cargo_name] = cargos.get(cargo_name, 0) + row[1]
        
        # Panamá
        if pais is None or pais.upper() in ["PANAMA", "PAN", "TODOS"]:
            cursor.execute(f"SELECT cargo, COUNT(cargo) as total FROM PlantaActivaPan{where_clause} GROUP BY cargo", params)
            for row in cursor.fetchall():
                cargo_name = row[0] or "Sin dato"
                cargos[cargo_name] = cargos.get(cargo_name, 0) + row[1]
        
        cursor.close()
        conn.close()
        
        resultado = [{"cargo": k, "cantidad": v} 
                     for k, v in sorted(cargos.items(), key=lambda x: x[1], reverse=True)]
        return resultado[:10]  # Top 10
        
    except Exception as e:
        logger.error(f"Error obteniendo detalle cargos: {e}")
        return []


def obtener_detalle_tipo_cargo(pais: str = None, mes: int = None, anio: int = None) -> list:
    """
    Obtiene distribución por tipo de cargo.
    SELECT tipo_cargo, COUNT(tipo_cargo) as total FROM PlantaActivaCol GROUP BY tipo_cargo
    Para Panamá: SELECT compania, COUNT(compania) as total FROM PlantaActivaPan GROUP BY compania
    """
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        where_clause = ""
        params = []
        if mes and anio:
            where_clause = " WHERE MONTH(fecha_corte) = ? AND YEAR(fecha_corte) = ?"
            params = [mes, anio]
        
        tipos_cargo = {}
        
        # Colombia
        if pais is None or pais.upper() in ["COLOMBIA", "COL", "TODOS"]:
            cursor.execute(f"SELECT tipo_cargo, COUNT(tipo_cargo) as total FROM PlantaActivaCol{where_clause} GROUP BY tipo_cargo", params)
            for row in cursor.fetchall():
                tipo = row[0] or "Sin dato"
                tipos_cargo[tipo] = tipos_cargo.get(tipo, 0) + row[1]
        
        # Perú
        if pais is None or pais.upper() in ["PERU", "PER", "TODOS"]:
            cursor.execute(f"SELECT tipo_cargo, COUNT(tipo_cargo) as total FROM PlantaActivaPer{where_clause} GROUP BY tipo_cargo", params)
            for row in cursor.fetchall():
                tipo = row[0] or "Sin dato"
                tipos_cargo[tipo] = tipos_cargo.get(tipo, 0) + row[1]
        
        # Panamá (usa compania en lugar de tipo_cargo)
        if pais is None or pais.upper() in ["PANAMA", "PAN", "TODOS"]:
            cursor.execute(f"SELECT compania, COUNT(compania) as total FROM PlantaActivaPan{where_clause} GROUP BY compania", params)
            for row in cursor.fetchall():
                tipo = row[0] or "Sin dato"
                tipos_cargo[tipo] = tipos_cargo.get(tipo, 0) + row[1]
        
        cursor.close()
        conn.close()
        
        resultado = [{"tipo": k, "cantidad": v} 
                     for k, v in sorted(tipos_cargo.items(), key=lambda x: x[1], reverse=True)]
        return resultado
        
    except Exception as e:
        logger.error(f"Error obteniendo detalle tipo cargo: {e}")
        return []
