"""
DAL para Carga de Recaudo
Funciones para manejar cargas desde Excel/Staging
"""
from typing import List, Optional, Dict, Any
import logging
from database import execute_query, execute_sp, get_db_connection, DatabaseError

logger = logging.getLogger(__name__)


def sp_cargar_desde_staging(
    nombre_archivo: str,
    id_usuario_carga: int,
    ruta_archivo: Optional[str] = None,
    origen: str = "EXCEL",
    periodo_anio_mes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Llama al SP SP_CampanasRecaudoQA_CargarDesdeStaging.
    
    Este SP:
    - Lee datos de CampanasRecaudoStagingQA
    - Mapea nombres de campañas
    - Limpia valores numéricos
    - Hace MERGE sobre CampanasRecaudoDiarioQA
    - Registra la carga en CampanasRecaudoCargaQA
    
    Args:
        nombre_archivo: Nombre del archivo Excel cargado
        id_usuario_carga: ID del usuario que realiza la carga
        ruta_archivo: Ruta completa del archivo (opcional)
        origen: Origen de los datos (EXCEL, APP, API)
        periodo_anio_mes: Periodo específico YYYY-MM (opcional, si no se pasa toma el mín del staging)
    
    Returns:
        Dict con IDCargaRecaudoQA y FilasAfectadas
    """
    params = {
        "NombreArchivo": nombre_archivo,
        "IDUsuarioCarga": id_usuario_carga,
        "Origen": origen
    }
    
    if ruta_archivo:
        params["RutaArchivo"] = ruta_archivo
    
    if periodo_anio_mes:
        params["PeriodoAnioMes"] = periodo_anio_mes
    
    try:
        logger.info(f"Ejecutando carga desde staging: {nombre_archivo}")
        result = execute_sp("SP_CampanasRecaudoQA_CargarDesdeStaging", params)
        
        # El SP devuelve IDCargaRecaudoQA y FilasAfectadas
        if result.get("rows"):
            row = result["rows"][0]
            return {
                "IDCargaRecaudoQA": row.get("IDCargaRecaudoQA"),
                "FilasAfectadas": row.get("FilasAfectadas", result.get("rowcount", 0)),
                "PeriodoAnioMes": periodo_anio_mes
            }
        
        return {
            "IDCargaRecaudoQA": None,
            "FilasAfectadas": result.get("rowcount", 0),
            "PeriodoAnioMes": periodo_anio_mes
        }
        
    except DatabaseError as e:
        logger.error(f"Error en SP_CargarDesdeStaging: {e}")
        raise


def get_cargas_recaudo(
    id_usuario: Optional[int] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    limite: int = 100
) -> List[dict]:
    """
    Obtiene el historial de cargas de recaudo.
    
    Args:
        id_usuario: Filtrar por usuario específico
        fecha_desde: Fecha desde (YYYY-MM-DD)
        fecha_hasta: Fecha hasta (YYYY-MM-DD)
        limite: Número máximo de registros
    
    Returns:
        Lista de cargas
    """
    conditions = []
    params = []
    
    if id_usuario:
        conditions.append("c.IDUsuarioCarga = ?")
        params.append(id_usuario)
    
    if fecha_desde:
        conditions.append("c.FechaCarga >= ?")
        params.append(fecha_desde)
    
    if fecha_hasta:
        conditions.append("c.FechaCarga <= ?")
        params.append(fecha_hasta)
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    sql = f"""
        SELECT TOP {limite}
            c.IDCargaRecaudoQA,
            c.PeriodoAnioMes,
            c.NombreArchivo,
            c.RutaArchivo,
            c.FechaCarga,
            c.IDUsuarioCarga,
            u.NombreUsuarioQA AS NombreUsuario,
            c.Origen,
            c.Observaciones
        FROM dbo.CampanasRecaudoCargaQA c
        LEFT JOIN dbo.UsuariosQA u ON c.IDUsuarioCarga = u.IDUsuarioQA
        {where_clause}
        ORDER BY c.FechaCarga DESC
    """
    try:
        return execute_query(sql, tuple(params) if params else None)
    except DatabaseError as e:
        logger.error(f"Error al obtener cargas: {e}")
        raise


def get_carga_by_id(id_carga: int) -> Optional[dict]:
    """
    Obtiene una carga por su ID.
    
    Args:
        id_carga: ID de la carga
    
    Returns:
        Diccionario con datos de la carga o None
    """
    sql = """
        SELECT 
            c.IDCargaRecaudoQA,
            c.PeriodoAnioMes,
            c.NombreArchivo,
            c.RutaArchivo,
            c.FechaCarga,
            c.IDUsuarioCarga,
            u.NombreUsuarioQA AS NombreUsuario,
            c.Origen,
            c.Observaciones
        FROM dbo.CampanasRecaudoCargaQA c
        LEFT JOIN dbo.UsuariosQA u ON c.IDUsuarioCarga = u.IDUsuarioQA
        WHERE c.IDCargaRecaudoQA = ?
    """
    try:
        results = execute_query(sql, (id_carga,))
        return results[0] if results else None
    except DatabaseError as e:
        logger.error(f"Error al obtener carga {id_carga}: {e}")
        raise


def get_registros_por_carga(id_carga: int) -> List[dict]:
    """
    Obtiene los registros de recaudo asociados a una carga.
    
    Args:
        id_carga: ID de la carga
    
    Returns:
        Lista de registros de recaudo de esa carga
    """
    sql = """
        SELECT 
            r.IDRecaudoQA,
            c.NombreCampana,
            i.NombreInversionistaQA,
            r.AnioMes,
            r.DiaHabil,
            r.ValorRecaudo,
            r.Meta,
            r.FechaCreacion
        FROM dbo.CampanasRecaudoDiarioQA r
        INNER JOIN dbo.CampanasInversionistasQA ci ON r.IDCampanasInversionistasQA = ci.IDCampanasInversionistasQA
        INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        WHERE r.IDCargaRecaudoQA = ?
        ORDER BY c.NombreCampana, i.NombreInversionistaQA, r.DiaHabil
    """
    try:
        return execute_query(sql, (id_carga,))
    except DatabaseError as e:
        logger.error(f"Error al obtener registros de carga {id_carga}: {e}")
        raise


# =============================================================================
# FUNCIONES PARA STAGING
# =============================================================================

def limpiar_staging() -> int:
    """
    Limpia la tabla de staging.
    
    Returns:
        Número de filas eliminadas
    """
    sql = "DELETE FROM dbo.CampanasRecaudoStagingQA"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        rowcount = cursor.rowcount
        conn.commit()
        cursor.close()
        logger.info(f"Staging limpiado: {rowcount} filas eliminadas")
        return rowcount


def insertar_en_staging(filas: List[dict]) -> int:
    """
    Inserta filas en la tabla de staging.
    
    Args:
        filas: Lista de diccionarios con datos del Excel
            Cada fila debe tener: Campana, AnioMes, DiaHabil, ValorRecaudo, Inversionista, Meta
    
    Returns:
        Número de filas insertadas
    """
    if not filas:
        return 0
    
    sql = """
        INSERT INTO dbo.CampanasRecaudoStagingQA 
            (Campana, AnioMes, DiaHabil, ValorRecaudo, Inversionista, Meta)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        count = 0
        for fila in filas:
            cursor.execute(sql, (
                fila.get("Campana"),
                fila.get("AnioMes"),
                fila.get("DiaHabil"),
                fila.get("ValorRecaudo"),
                fila.get("Inversionista"),
                fila.get("Meta")
            ))
            count += 1
        conn.commit()
        cursor.close()
        logger.info(f"Staging: {count} filas insertadas")
        return count


def contar_staging() -> int:
    """
    Cuenta las filas en staging.
    
    Returns:
        Número de filas en staging
    """
    sql = "SELECT COUNT(*) AS Total FROM dbo.CampanasRecaudoStagingQA"
    try:
        results = execute_query(sql)
        return results[0]["Total"] if results else 0
    except DatabaseError as e:
        logger.error(f"Error al contar staging: {e}")
        raise


def get_staging_preview(limite: int = 100) -> List[dict]:
    """
    Obtiene una vista previa de los datos en staging.
    
    Args:
        limite: Número máximo de filas
    
    Returns:
        Lista de filas del staging
    """
    sql = f"""
        SELECT TOP {limite}
            Campana,
            AnioMes,
            DiaHabil,
            ValorRecaudo,
            Inversionista,
            Meta
        FROM dbo.CampanasRecaudoStagingQA
        ORDER BY Campana, Inversionista, AnioMes, DiaHabil
    """
    try:
        return execute_query(sql)
    except DatabaseError as e:
        logger.error(f"Error al obtener preview de staging: {e}")
        raise


# =============================================================================
# FUNCIONES DE AUDITORÍA
# =============================================================================

def get_auditoria_recaudo(
    id_recaudo: Optional[int] = None,
    id_carga: Optional[int] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    limite: int = 100
) -> List[dict]:
    """
    Obtiene registros de auditoría.
    
    Args:
        id_recaudo: Filtrar por registro de recaudo
        id_carga: Filtrar por carga
        fecha_desde: Fecha desde
        fecha_hasta: Fecha hasta
        limite: Límite de registros
    
    Returns:
        Lista de registros de auditoría
    """
    conditions = []
    params = []
    
    if id_recaudo:
        conditions.append("a.IDRecaudoQA = ?")
        params.append(id_recaudo)
    
    if id_carga:
        conditions.append("a.IDCargaRecaudoQA = ?")
        params.append(id_carga)
    
    if fecha_desde:
        conditions.append("a.FechaEvento >= ?")
        params.append(fecha_desde)
    
    if fecha_hasta:
        conditions.append("a.FechaEvento <= ?")
        params.append(fecha_hasta)
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    sql = f"""
        SELECT TOP {limite}
            a.IDAuditoriaRecaudoQA,
            a.IDRecaudoQA,
            a.IDCargaRecaudoQA,
            a.FechaEvento,
            a.IDUsuarioEvento,
            u.NombreUsuarioQA AS NombreUsuario,
            a.TipoOperacion,
            a.ValorRecaudo_Anterior,
            a.ValorRecaudo_Nuevo,
            a.Meta_Anterior,
            a.Meta_Nuevo,
            a.Origen,
            a.Observaciones
        FROM dbo.CampanasRecaudoAuditoriaQA a
        LEFT JOIN dbo.UsuariosQA u ON a.IDUsuarioEvento = u.IDUsuarioQA
        {where_clause}
        ORDER BY a.FechaEvento DESC
    """
    try:
        return execute_query(sql, tuple(params) if params else None)
    except DatabaseError as e:
        logger.error(f"Error al obtener auditoría: {e}")
        raise
