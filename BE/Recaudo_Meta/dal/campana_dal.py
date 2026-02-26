"""
DAL para Campañas
Funciones de acceso a datos para la tabla CampanasQA
"""
from typing import List, Optional
import logging
from database import execute_query, execute_sp, DatabaseError

logger = logging.getLogger(__name__)


def get_all_campanas(solo_activas: bool = True) -> List[dict]:
    """
    Obtiene todas las campañas.
    
    Args:
        solo_activas: Si solo retorna campañas activas (por defecto True)
    
    Returns:
        Lista de diccionarios con datos de campañas
    """
    sql = """
        SELECT 
            IDCampanasQA,
            NombreCampana,
            FechaCreacion,
            IDUsuarioLider
        FROM dbo.CampanasQA
        ORDER BY NombreCampana
    """
    try:
        return execute_query(sql)
    except DatabaseError as e:
        logger.error(f"Error al obtener campañas: {e}")
        raise


def get_campana_by_id(id_campana: int) -> Optional[dict]:
    """
    Obtiene una campaña por su ID.
    
    Args:
        id_campana: ID de la campaña
    
    Returns:
        Diccionario con datos de la campaña o None
    """
    sql = """
        SELECT 
            IDCampanasQA,
            NombreCampana,
            FechaCreacion,
            IDUsuarioLider
        FROM dbo.CampanasQA
        WHERE IDCampanasQA = ?
    """
    try:
        results = execute_query(sql, (id_campana,))
        return results[0] if results else None
    except DatabaseError as e:
        logger.error(f"Error al obtener campaña {id_campana}: {e}")
        raise


def get_campana_by_nombre(nombre: str) -> Optional[dict]:
    """
    Obtiene una campaña por su nombre.
    
    Args:
        nombre: Nombre de la campaña
    
    Returns:
        Diccionario con datos de la campaña o None
    """
    sql = """
        SELECT 
            IDCampanasQA,
            NombreCampana,
            FechaCreacion,
            IDUsuarioLider
        FROM dbo.CampanasQA
        WHERE NombreCampana = ?
    """
    try:
        results = execute_query(sql, (nombre,))
        return results[0] if results else None
    except DatabaseError as e:
        logger.error(f"Error al obtener campaña por nombre {nombre}: {e}")
        raise


def get_campanas_con_inversionistas() -> List[dict]:
    """
    Obtiene campañas con sus inversionistas asociados.
    
    Returns:
        Lista de diccionarios con campaña y sus inversionistas
    """
    sql = """
        SELECT DISTINCT
            c.IDCampanasQA,
            c.NombreCampana,
            ci.IDCampanasInversionistasQA,
            i.IDInversionistaQA,
            i.NombreInversionistaQA
        FROM dbo.CampanasQA c
        INNER JOIN dbo.CampanasInversionistasQA ci ON c.IDCampanasQA = ci.IDCampanasQA
        INNER JOIN dbo.InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
        WHERE ci.EsActivo = 1 AND i.EsActivo = 1
        ORDER BY c.NombreCampana, i.NombreInversionistaQA
    """
    try:
        return execute_query(sql)
    except DatabaseError as e:
        logger.error(f"Error al obtener campañas con inversionistas: {e}")
        raise


def get_campanas_por_rol(id_rol: int) -> List[dict]:
    """
    Obtiene campañas asociadas a un rol.
    
    Args:
        id_rol: ID del rol
    
    Returns:
        Lista de campañas asociadas al rol
    """
    sql = """
        SELECT 
            c.IDCampanasQA,
            c.NombreCampana,
            c.FechaCreacion,
            cr.IDCampanasRolesQA
        FROM dbo.CampanasQA c
        INNER JOIN dbo.CampanasRolesQA cr ON c.IDCampanasQA = cr.IDCampanasQA
        WHERE cr.IDRol = ?
        ORDER BY c.NombreCampana
    """
    try:
        return execute_query(sql, (id_rol,))
    except DatabaseError as e:
        logger.error(f"Error al obtener campañas por rol {id_rol}: {e}")
        raise
