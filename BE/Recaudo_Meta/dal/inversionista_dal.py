"""
DAL para Inversionistas
Funciones de acceso a datos para las tablas InversionistaQA y CampanasInversionistasQA
"""
from typing import List, Optional
import logging
from database import execute_query, execute_sp, DatabaseError

logger = logging.getLogger(__name__)


def get_all_inversionistas(solo_activos: bool = True) -> List[dict]:
    """
    Obtiene todos los inversionistas.
    
    Args:
        solo_activos: Si solo retorna inversionistas activos
    
    Returns:
        Lista de diccionarios con datos de inversionistas
    """
    sql = """
        SELECT 
            IDInversionistaQA,
            NombreInversionistaQA,
            EsActivo,
            FechaCreacion,
            IDUsuarioCreacion
        FROM dbo.InversionistaQA
        WHERE (@solo_activos = 0 OR EsActivo = 1)
        ORDER BY NombreInversionistaQA
    """
    # Reemplazar parámetro porque SQL Server no acepta BIT directamente
    if solo_activos:
        sql = sql.replace("(@solo_activos = 0 OR EsActivo = 1)", "EsActivo = 1")
    else:
        sql = sql.replace("(@solo_activos = 0 OR EsActivo = 1)", "1=1")
    
    try:
        return execute_query(sql)
    except DatabaseError as e:
        logger.error(f"Error al obtener inversionistas: {e}")
        raise


def get_inversionista_by_id(id_inversionista: int) -> Optional[dict]:
    """
    Obtiene un inversionista por su ID.
    
    Args:
        id_inversionista: ID del inversionista
    
    Returns:
        Diccionario con datos del inversionista o None
    """
    sql = """
        SELECT 
            IDInversionistaQA,
            NombreInversionistaQA,
            EsActivo,
            FechaCreacion,
            IDUsuarioCreacion
        FROM dbo.InversionistaQA
        WHERE IDInversionistaQA = ?
    """
    try:
        results = execute_query(sql, (id_inversionista,))
        return results[0] if results else None
    except DatabaseError as e:
        logger.error(f"Error al obtener inversionista {id_inversionista}: {e}")
        raise


def get_inversionista_by_nombre(nombre: str) -> Optional[dict]:
    """
    Obtiene un inversionista por su nombre.
    
    Args:
        nombre: Nombre del inversionista
    
    Returns:
        Diccionario con datos del inversionista o None
    """
    sql = """
        SELECT 
            IDInversionistaQA,
            NombreInversionistaQA,
            EsActivo,
            FechaCreacion,
            IDUsuarioCreacion
        FROM dbo.InversionistaQA
        WHERE NombreInversionistaQA = ?
    """
    try:
        results = execute_query(sql, (nombre,))
        return results[0] if results else None
    except DatabaseError as e:
        logger.error(f"Error al obtener inversionista por nombre {nombre}: {e}")
        raise


def get_inversionistas_por_campana(id_campana: int, solo_activos: bool = True) -> List[dict]:
    """
    Obtiene los inversionistas asociados a una campaña.
    
    Args:
        id_campana: ID de la campaña
        solo_activos: Si solo retorna activos
    
    Returns:
        Lista de inversionistas de la campaña
    """
    where_activos = "AND ci.EsActivo = 1 AND i.EsActivo = 1" if solo_activos else ""
    sql = f"""
        SELECT 
            i.IDInversionistaQA,
            i.NombreInversionistaQA,
            i.EsActivo,
            ci.IDCampanasInversionistasQA,
            ci.FechaCreacion AS FechaAsociacion
        FROM dbo.InversionistaQA i
        INNER JOIN dbo.CampanasInversionistasQA ci ON i.IDInversionistaQA = ci.IDInversionistaQA
        WHERE ci.IDCampanasQA = ? {where_activos}
        ORDER BY i.NombreInversionistaQA
    """
    try:
        return execute_query(sql, (id_campana,))
    except DatabaseError as e:
        logger.error(f"Error al obtener inversionistas de campaña {id_campana}: {e}")
        raise


def get_campana_inversionista(id_campana: int, id_inversionista: int) -> Optional[dict]:
    """
    Obtiene la relación campaña-inversionista.
    
    Args:
        id_campana: ID de la campaña
        id_inversionista: ID del inversionista
    
    Returns:
        Diccionario con datos de la relación o None
    """
    sql = """
        SELECT 
            ci.IDCampanasInversionistasQA,
            ci.IDCampanasQA,
            ci.IDInversionistaQA,
            ci.EsActivo,
            ci.FechaCreacion,
            c.NombreCampana,
            i.NombreInversionistaQA
        FROM dbo.CampanasInversionistasQA ci
        INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        WHERE ci.IDCampanasQA = ? AND ci.IDInversionistaQA = ?
    """
    try:
        results = execute_query(sql, (id_campana, id_inversionista))
        return results[0] if results else None
    except DatabaseError as e:
        logger.error(f"Error al obtener relación campaña-inversionista: {e}")
        raise


def get_campana_inversionista_by_id(id_relacion: int) -> Optional[dict]:
    """
    Obtiene la relación campaña-inversionista por su ID.
    
    Args:
        id_relacion: ID de la relación
    
    Returns:
        Diccionario con datos de la relación o None
    """
    sql = """
        SELECT 
            ci.IDCampanasInversionistasQA,
            ci.IDCampanasQA,
            ci.IDInversionistaQA,
            ci.EsActivo,
            ci.FechaCreacion,
            c.NombreCampana,
            i.NombreInversionistaQA
        FROM dbo.CampanasInversionistasQA ci
        INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        WHERE ci.IDCampanasInversionistasQA = ?
    """
    try:
        results = execute_query(sql, (id_relacion,))
        return results[0] if results else None
    except DatabaseError as e:
        logger.error(f"Error al obtener relación por ID {id_relacion}: {e}")
        raise


def get_all_campanas_inversionistas(solo_activos: bool = True) -> List[dict]:
    """
    Obtiene todas las relaciones campaña-inversionista.
    
    Args:
        solo_activos: Si solo retorna relaciones activas
    
    Returns:
        Lista de todas las relaciones
    """
    where_activos = "WHERE ci.EsActivo = 1 AND i.EsActivo = 1" if solo_activos else ""
    sql = f"""
        SELECT 
            ci.IDCampanasInversionistasQA,
            ci.IDCampanasQA,
            c.NombreCampana,
            ci.IDInversionistaQA,
            i.NombreInversionistaQA,
            ci.EsActivo
        FROM dbo.CampanasInversionistasQA ci
        INNER JOIN dbo.CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
        INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        {where_activos}
        ORDER BY c.NombreCampana, i.NombreInversionistaQA
    """
    try:
        return execute_query(sql)
    except DatabaseError as e:
        logger.error(f"Error al obtener todas las relaciones: {e}")
        raise
