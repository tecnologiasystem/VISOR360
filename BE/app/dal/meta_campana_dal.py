# DAL para metas de campañas pequeñas (subcampañas/inversionistas)

from app.database import get_connection1
from typing import List, Dict, Optional


def obtener_metas_campana_pequena(nombre_pais: str, mes: int, anio: int) -> List[Dict]:
    """
    Obtiene todas las metas de subcampañas para un país en un mes específico
    """
    conn = get_connection1()
    cursor = conn.cursor()

    query = """
        SELECT 
            id_meta_campana,
            nombre_pais,
            nombre_campana_pequena,
            mes,
            anio,
            meta_valor,
            fecha_creacion,
            fecha_modificacion,
            usuario_creacion,
            usuario_modificacion,
            recaudo_manual
        FROM metas_campana_pequena
        WHERE nombre_pais = ?
        AND mes = ?
        AND anio = ?
        ORDER BY nombre_campana_pequena
    """

    cursor.execute(query, (nombre_pais, mes, anio))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    resultado = []
    for row in rows:
        resultado.append(
            {
                "id_meta": row[0],
                "nombre_pais": row[1],
                "nombre_campana": row[2],
                "mes": row[3],
                "anio": row[4],
                "meta_valor": float(row[5]) if row[5] else 0.0,
                "fecha_creacion": row[6].isoformat() if row[6] else None,
                "fecha_modificacion": row[7].isoformat() if row[7] else None,
                "usuario_creacion": row[8],
                "usuario_modificacion": row[9],
                "recaudo_manual": float(row[10]) if row[10] else 0.0,
            }
        )

    return resultado


def obtener_meta_total_pais(nombre_pais: str, mes: int, anio: int) -> float:
    """
    Calcula la meta total de un país sumando las metas de todas sus subcampañas
    """
    conn = get_connection1()
    cursor = conn.cursor()

    query = """
        SELECT COALESCE(SUM(meta_valor), 0) as meta_total
        FROM metas_campana_pequena
        WHERE nombre_pais = ?
        AND mes = ?
        AND anio = ?
    """

    cursor.execute(query, (nombre_pais, mes, anio))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return float(row[0]) if row and row[0] else 0.0


def obtener_meta_campana_especifica(
    nombre_pais: str, nombre_campana: str, mes: int, anio: int
) -> Optional[float]:
    """
    Obtiene la meta de una subcampaña específica
    """
    conn = get_connection1()
    cursor = conn.cursor()

    query = """
        SELECT meta_valor
        FROM metas_campana_pequena
        WHERE nombre_pais = ?
        AND nombre_campana_pequena = ?
        AND mes = ?
        AND anio = ?
    """

    cursor.execute(query, (nombre_pais, nombre_campana, mes, anio))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return float(row[0]) if row and row[0] else None


def crear_meta_campana(
    nombre_pais: str,
    nombre_campana: str,
    mes: int,
    anio: int,
    meta_valor: float,
    usuario: str = None,
    recaudo_manual: float = 0.0,
) -> int:
    """
    Crea o actualiza una meta para una subcampaña
    """
    conn = get_connection1()
    cursor = conn.cursor()

    # Verificar si ya existe
    query_check = """
        SELECT id_meta_campana 
        FROM metas_campana_pequena
        WHERE nombre_pais = ?
        AND nombre_campana_pequena = ?
        AND mes = ?
        AND anio = ?
    """

    cursor.execute(query_check, (nombre_pais, nombre_campana, mes, anio))
    existing = cursor.fetchone()

    if existing:
        # Actualizar
        query_update = """
            UPDATE metas_campana_pequena
            SET meta_valor = ?,
                fecha_modificacion = GETDATE(),
                usuario_modificacion = ?,
                recaudo_manual = ?
            WHERE id_meta_campana = ?
        """
        cursor.execute(query_update, (meta_valor, usuario, recaudo_manual, existing[0]))
        conn.commit()
        meta_id = existing[0]
    else:
        # Insertar
        query_insert = """
            INSERT INTO metas_campana_pequena 
            (nombre_pais, nombre_campana_pequena, mes, anio, meta_valor, usuario_creacion, recaudo_manual)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            query_insert, (nombre_pais, nombre_campana, mes, anio, meta_valor, usuario, recaudo_manual)
        )
        conn.commit()

        # Obtener el ID insertado
        cursor.execute("SELECT @@IDENTITY")
        meta_id = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return meta_id


def eliminar_meta_campana(
    nombre_pais: str, nombre_campana: str, mes: int, anio: int
) -> bool:
    """
    Elimina una meta de subcampaña
    """
    conn = get_connection1()
    cursor = conn.cursor()

    query = """
        DELETE FROM metas_campana_pequena
        WHERE nombre_pais = ?
        AND nombre_campana_pequena = ?
        AND mes = ?
        AND anio = ?
    """

    cursor.execute(query, (nombre_pais, nombre_campana, mes, anio))
    rows_affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    return rows_affected > 0
