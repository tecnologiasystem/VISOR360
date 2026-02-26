"""
BLL para Planta Activa - Radar de Talento Humano.
Lógica de negocio para procesar datos de empleados.
"""

from app.dal.planta_activa_dal import (
    obtener_estadisticas_por_pais,
    obtener_estadisticas_todos_paises,
    obtener_estadisticas_colombia,
    obtener_estadisticas_peru,
    obtener_estadisticas_panama,
    obtener_detalle_unidades,
    obtener_detalle_contratos,
    obtener_detalle_departamentos,
    obtener_detalle_cargos,
    obtener_detalle_tipo_cargo
)
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def obtener_resumen_completo(pais: str = None, mes: int = None, anio: int = None) -> Dict:
    """
    Obtiene el resumen completo de estadísticas de planta activa.
    
    Args:
        pais: "COLOMBIA", "PERU", "PANAMA" o None para todos
        mes: Mes de corte (1-12), opcional
        anio: Año de corte, opcional
    
    Returns:
        Dict con:
        - personal_activo (card 1)
        - costo_recurso_humano (card 2)
        - generos: {genero: cantidad} (card 3)
        - edad_promedio (card 4)
        - por_unidad: lista de unidades
        - por_contrato: lista de contratos
        - por_departamento: lista de departamentos
    """
    try:
        if pais is None or pais.upper() == "TODOS":
            base = obtener_estadisticas_todos_paises(mes, anio)
        else:
            base = obtener_estadisticas_por_pais(pais, mes, anio)
        
        # Agregar detalles
        base["por_unidad"] = obtener_detalle_unidades(pais, mes, anio)
        base["por_contrato"] = obtener_detalle_contratos(pais, mes, anio)
        base["por_departamento"] = obtener_detalle_departamentos(pais, mes, anio)
        base["por_cargo"] = obtener_detalle_cargos(pais, mes, anio)
        base["por_tipo_cargo"] = obtener_detalle_tipo_cargo(pais, mes, anio)
        
        return base
        
    except Exception as e:
        logger.error(f"Error en obtener_resumen_completo: {e}")
        raise


def obtener_lista_paises() -> list:
    """
    Obtiene la lista de países disponibles.
    """
    return ["COLOMBIA", "PERU", "PANAMA"]

