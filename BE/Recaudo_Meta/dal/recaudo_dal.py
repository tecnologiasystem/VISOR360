"""
DAL para Recaudo Diario
Funciones de acceso a datos para la tabla CampanasRecaudoDiarioQA
Incluye llamadas a los stored procedures CRUD y ConsultaFE
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
import logging
from database import execute_query, execute_sp, get_db_cursor, DatabaseError

logger = logging.getLogger(__name__)


# =============================================================================
# FUNCIONES CRUD DIRECTAS
# =============================================================================

def get_recaudo_by_id(id_recaudo: int) -> Optional[dict]:
    """
    Obtiene un registro de recaudo por su ID.
    
    Args:
        id_recaudo: ID del registro
    
    Returns:
        Diccionario con datos del recaudo o None
    """
    sql = """
        SELECT 
            r.IDRecaudoQA,
            r.IDCampanasInversionistasQA,
            r.AnioMes,
            r.DiaHabil,
            r.ValorRecaudo,
            r.Meta,
            r.IDCargaRecaudoQA,
            r.FechaCreacion,
            r.IDUsuarioCreacion,
            r.FechaUltimaActualizacion,
            r.IDUsuarioUltimaActualizacion,
            r.EsActivo,
            c.IDCampanasQA,
            c.NombreCampana,
            i.IDInversionistaQA,
            i.NombreInversionistaQA
        FROM dbo.CampanasRecaudoDiarioQA r
        INNER JOIN dbo.CampanasInversionistasQA ci ON r.IDCampanasInversionistasQA = ci.IDCampanasInversionistasQA
        INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        WHERE r.IDRecaudoQA = ?
    """
    try:
        results = execute_query(sql, (id_recaudo,))
        return results[0] if results else None
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo {id_recaudo}: {e}")
        raise


def get_recaudo_por_campana_inversionista_periodo(
    id_campana_inversionista: int,
    anio_mes: str,
    dia_habil: Optional[int] = None
) -> List[dict]:
    """
    Obtiene registros de recaudo por campaña-inversionista y periodo.
    
    Args:
        id_campana_inversionista: ID de la relación
        anio_mes: Periodo YYYY-MM
        dia_habil: Día hábil específico (opcional)
    
    Returns:
        Lista de registros de recaudo
    """
    params = [id_campana_inversionista, anio_mes]
    where_dia = ""
    if dia_habil is not None:
        where_dia = "AND r.DiaHabil = ?"
        params.append(dia_habil)
    
    sql = f"""
        SELECT 
            r.IDRecaudoQA,
            r.IDCampanasInversionistasQA,
            r.AnioMes,
            r.DiaHabil,
            r.ValorRecaudo,
            r.Meta,
            r.EsActivo
        FROM dbo.CampanasRecaudoDiarioQA r
        WHERE r.IDCampanasInversionistasQA = ?
          AND r.AnioMes = ?
          AND r.EsActivo = 1
          {where_dia}
        ORDER BY r.DiaHabil
    """
    try:
        return execute_query(sql, tuple(params))
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo por relación: {e}")
        raise


def listar_recaudo_diario(
    id_campana: Optional[int] = None,
    id_inversionista: Optional[int] = None,
    anio_mes: Optional[str] = None,
    anio_mes_desde: Optional[str] = None,
    anio_mes_hasta: Optional[str] = None,
    solo_activos: bool = True
) -> List[dict]:
    """
    Lista registros de recaudo diario con filtros opcionales.
    
    Returns:
        Lista de registros de recaudo
    """
    conditions = []
    params = []
    
    if solo_activos:
        conditions.append("r.EsActivo = 1")
    
    if id_campana:
        conditions.append("c.IDCampanasQA = ?")
        params.append(id_campana)
    
    if id_inversionista:
        conditions.append("i.IDInversionistaQA = ?")
        params.append(id_inversionista)
    
    if anio_mes:
        conditions.append("r.AnioMes = ?")
        params.append(anio_mes)
    elif anio_mes_desde and anio_mes_hasta:
        conditions.append("r.AnioMes BETWEEN ? AND ?")
        params.extend([anio_mes_desde, anio_mes_hasta])
    elif anio_mes_desde:
        conditions.append("r.AnioMes >= ?")
        params.append(anio_mes_desde)
    elif anio_mes_hasta:
        conditions.append("r.AnioMes <= ?")
        params.append(anio_mes_hasta)
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    sql = f"""
        SELECT 
            r.IDRecaudoQA,
            r.IDCampanasInversionistasQA,
            c.IDCampanasQA,
            c.NombreCampana,
            i.IDInversionistaQA,
            i.NombreInversionistaQA,
            r.AnioMes,
            r.DiaHabil,
            r.ValorRecaudo,
            r.Meta,
            r.EsActivo
        FROM dbo.CampanasRecaudoDiarioQA r
        INNER JOIN dbo.CampanasInversionistasQA ci ON r.IDCampanasInversionistasQA = ci.IDCampanasInversionistasQA
        INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        {where_clause}
        ORDER BY r.AnioMes, c.NombreCampana, i.NombreInversionistaQA, r.DiaHabil
    """
    try:
        return execute_query(sql, tuple(params) if params else None)
    except DatabaseError as e:
        logger.error(f"Error al listar recaudo diario: {e}")
        raise


# =============================================================================
# FUNCIONES VÍA STORED PROCEDURES
# =============================================================================

def sp_crud_recaudo(
    accion: int,
    id_recaudo: Optional[int] = None,
    id_campana_inversionista: Optional[int] = None,
    anio_mes: Optional[str] = None,
    dia_habil: Optional[int] = None,
    valor_recaudo: Optional[Decimal] = None,
    meta: Optional[Decimal] = None,
    id_usuario: Optional[int] = None,
    id_carga: Optional[int] = None
) -> Dict[str, Any]:
    """
    Llama al SP SP_CampanasRecaudoDiarioQA_CRUD.
    
    Args:
        accion: 1=INSERT, 2=UPDATE, 3=DELETE, 4=GET BY ID, 5=LISTAR
        id_recaudo: ID del registro (para UPDATE, DELETE, GET)
        id_campana_inversionista: ID de relación (para INSERT)
        anio_mes: Periodo YYYY-MM
        dia_habil: Día hábil
        valor_recaudo: Valor del recaudo
        meta: Meta establecida
        id_usuario: ID del usuario que ejecuta
        id_carga: ID de la carga asociada
    
    Returns:
        Resultado del SP
    """
    params = {
        "Accion": accion,
        "IDRecaudoQA": id_recaudo,
        "IDCampanasInversionistasQA": id_campana_inversionista,
        "AnioMes": anio_mes,
        "DiaHabil": dia_habil,
        "ValorRecaudo": float(valor_recaudo) if valor_recaudo else None,
        "Meta": float(meta) if meta else None,
        "IDUsuario": id_usuario,
        "IDCargaRecaudoQA": id_carga
    }
    
    # Filtrar parámetros None
    params = {k: v for k, v in params.items() if v is not None}
    
    try:
        result = execute_sp("SP_CampanasRecaudoDiarioQA_CRUD", params)
        return result
    except DatabaseError as e:
        logger.error(f"Error en SP_CRUD acción {accion}: {e}")
        raise


def sp_consulta_fe_diario(
    id_campana: Optional[int] = None,
    id_inversionista: Optional[int] = None,
    anio_mes: Optional[str] = None,
    anio_mes_desde: Optional[str] = None,
    anio_mes_hasta: Optional[str] = None,
    solo_activos: bool = True
) -> List[dict]:
    """
    Llama al SP SP_CampanasRecaudoQA_ConsultaFE con TipoResumen=1 (DIARIO).
    
    Returns:
        Lista de resúmenes diarios
    """
    params = {
        "TipoResumen": 1,
        "SoloActivos": 1 if solo_activos else 0
    }
    
    if id_campana:
        params["IDCampanasQA"] = id_campana
    if id_inversionista:
        params["IDInversionistaQA"] = id_inversionista
    if anio_mes:
        params["AnioMes"] = anio_mes
    if anio_mes_desde:
        params["AnioMesDesde"] = anio_mes_desde
    if anio_mes_hasta:
        params["AnioMesHasta"] = anio_mes_hasta
    
    try:
        result = execute_sp("SP_CampanasRecaudoQA_ConsultaFE", params)
        return result.get("rows", [])
    except DatabaseError as e:
        logger.error(f"Error en SP_ConsultaFE_Diario: {e}")
        raise


def sp_consulta_fe_mensual(
    id_campana: Optional[int] = None,
    id_inversionista: Optional[int] = None,
    anio_mes: Optional[str] = None,
    anio_mes_desde: Optional[str] = None,
    anio_mes_hasta: Optional[str] = None,
    solo_activos: bool = True
) -> List[dict]:
    """
    Llama al SP SP_CampanasRecaudoQA_ConsultaFE con TipoResumen=2 (MENSUAL).
    
    Returns:
        Lista de resúmenes mensuales
    """
    params = {
        "TipoResumen": 2,
        "SoloActivos": 1 if solo_activos else 0
    }
    
    if id_campana:
        params["IDCampanasQA"] = id_campana
    if id_inversionista:
        params["IDInversionistaQA"] = id_inversionista
    if anio_mes:
        params["AnioMes"] = anio_mes
    if anio_mes_desde:
        params["AnioMesDesde"] = anio_mes_desde
    if anio_mes_hasta:
        params["AnioMesHasta"] = anio_mes_hasta
    
    try:
        result = execute_sp("SP_CampanasRecaudoQA_ConsultaFE", params)
        return result.get("rows", [])
    except DatabaseError as e:
        logger.error(f"Error en SP_ConsultaFE_Mensual: {e}")
        raise


# =============================================================================
# FUNCIONES AGREGADAS PARA DASHBOARD
# =============================================================================

def get_resumen_recaudo_por_campana(
    anio_mes: str,
    id_campana: Optional[int] = None
) -> List[dict]:
    """
    Obtiene resumen de recaudo agrupado por campaña para un mes.
    
    Args:
        anio_mes: Periodo YYYY-MM
        id_campana: ID de campaña específica (opcional)
    
    Returns:
        Lista con totales por campaña
    """
    where_campana = "AND c.IDCampanasQA = ?" if id_campana else ""
    params = [anio_mes]
    if id_campana:
        params.append(id_campana)
    
    sql = f"""
        SELECT 
            c.IDCampanasQA,
            c.NombreCampana,
            SUM(ISNULL(r.ValorRecaudo, 0)) AS TotalRecaudo,
            SUM(ISNULL(r.Meta, 0)) AS TotalMeta,
            SUM(ISNULL(r.ValorRecaudo, 0)) - SUM(ISNULL(r.Meta, 0)) AS Diferencia,
            CASE 
                WHEN SUM(ISNULL(r.Meta, 0)) > 0 
                THEN ROUND(SUM(ISNULL(r.ValorRecaudo, 0)) * 100.0 / SUM(r.Meta), 2)
                ELSE 0 
            END AS PorcentajeCumplimiento
        FROM dbo.CampanasRecaudoDiarioQA r
        INNER JOIN dbo.CampanasInversionistasQA ci ON r.IDCampanasInversionistasQA = ci.IDCampanasInversionistasQA
        INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        WHERE r.AnioMes = ? AND r.EsActivo = 1
        {where_campana}
        GROUP BY c.IDCampanasQA, c.NombreCampana
        ORDER BY c.NombreCampana
    """
    try:
        return execute_query(sql, tuple(params))
    except DatabaseError as e:
        logger.error(f"Error al obtener resumen por campaña: {e}")
        raise


def get_resumen_recaudo_por_inversionista(
    anio_mes: str,
    id_campana: Optional[int] = None
) -> List[dict]:
    """
    Obtiene resumen de recaudo agrupado por inversionista para un mes.
    
    Args:
        anio_mes: Periodo YYYY-MM
        id_campana: ID de campaña específica (opcional)
    
    Returns:
        Lista con totales por inversionista
    """
    where_campana = "AND c.IDCampanasQA = ?" if id_campana else ""
    params = [anio_mes]
    if id_campana:
        params.append(id_campana)
    
    sql = f"""
        SELECT 
            i.IDInversionistaQA,
            i.NombreInversionistaQA,
            SUM(ISNULL(r.ValorRecaudo, 0)) AS TotalRecaudo,
            SUM(ISNULL(r.Meta, 0)) AS TotalMeta,
            SUM(ISNULL(r.ValorRecaudo, 0)) - SUM(ISNULL(r.Meta, 0)) AS Diferencia,
            CASE 
                WHEN SUM(ISNULL(r.Meta, 0)) > 0 
                THEN ROUND(SUM(ISNULL(r.ValorRecaudo, 0)) * 100.0 / SUM(r.Meta), 2)
                ELSE 0 
            END AS PorcentajeCumplimiento
        FROM dbo.CampanasRecaudoDiarioQA r
        INNER JOIN dbo.CampanasInversionistasQA ci ON r.IDCampanasInversionistasQA = ci.IDCampanasInversionistasQA
        INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        WHERE r.AnioMes = ? AND r.EsActivo = 1
        {where_campana}
        GROUP BY i.IDInversionistaQA, i.NombreInversionistaQA
        ORDER BY i.NombreInversionistaQA
    """
    try:
        return execute_query(sql, tuple(params))
    except DatabaseError as e:
        logger.error(f"Error al obtener resumen por inversionista: {e}")
        raise


def get_acumulado_diario(
    anio_mes: str,
    id_campana: Optional[int] = None,
    id_inversionista: Optional[int] = None
) -> List[dict]:
    """
    Obtiene el acumulado diario de recaudo vs meta.
    
    Returns:
        Lista con acumulado por día hábil
    """
    conditions = ["r.AnioMes = ?", "r.EsActivo = 1"]
    params = [anio_mes]
    
    if id_campana:
        conditions.append("c.IDCampanasQA = ?")
        params.append(id_campana)
    
    if id_inversionista:
        conditions.append("i.IDInversionistaQA = ?")
        params.append(id_inversionista)
    
    where_clause = " AND ".join(conditions)
    
    sql = f"""
        WITH DiarioAgrupado AS (
            SELECT 
                r.DiaHabil,
                SUM(ISNULL(r.ValorRecaudo, 0)) AS RecaudoDia,
                SUM(ISNULL(r.Meta, 0)) AS MetaDia
            FROM dbo.CampanasRecaudoDiarioQA r
            INNER JOIN dbo.CampanasInversionistasQA ci ON r.IDCampanasInversionistasQA = ci.IDCampanasInversionistasQA
            INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
            INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
            WHERE {where_clause}
            GROUP BY r.DiaHabil
        )
        SELECT 
            DiaHabil,
            RecaudoDia,
            MetaDia,
            SUM(RecaudoDia) OVER (ORDER BY DiaHabil) AS RecaudoAcumulado,
            SUM(MetaDia) OVER (ORDER BY DiaHabil) AS MetaAcumulada
        FROM DiarioAgrupado
        ORDER BY DiaHabil
    """
    try:
        return execute_query(sql, tuple(params))
    except DatabaseError as e:
        logger.error(f"Error al obtener acumulado diario: {e}")
        raise
