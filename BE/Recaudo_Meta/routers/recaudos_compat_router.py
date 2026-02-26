"""
Router de compatibilidad para FE existente
Endpoints: /recaudos (plural) - compatible con el FE actual
Mapea las llamadas del FE a los servicios del microservicio
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from decimal import Decimal
import logging
from datetime import datetime, date

from bll.recaudo_bll import RecaudoService
from bll.campana_bll import CampanaService
from database import DatabaseError
from app.dal import portafolio_dal

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recaudos",
    tags=["Recaudos Compatibilidad FE"],
    responses={
        500: {"description": "Error interno del servidor"}
    }
)

# Mapeo de nombres de campaña a IDs
CAMPANA_NAME_TO_ID = {
    "NPL COL": 1,
    "NPL COLOMBIA": 1,
    "NPL PER": 3,
    "NPL PERU": 3,
    "NPL CHILE": 4,
    "ACC COL": 2,
    "ACC COLOMBIA": 2,
}


def _format_currency(value: float) -> str:
    """Formatear valor como moneda"""
    if value is None:
        return "$0"
    return f"${value:,.0f}"


def _get_campana_id(name: str) -> Optional[int]:
    """Obtener ID de campaña por nombre"""
    name_upper = name.upper().strip()
    return CAMPANA_NAME_TO_ID.get(name_upper)


def _extract_registros(resultado) -> List[Dict[str, Any]]:
    """Extrae registros de un resultado que puede ser Pydantic o dict"""
    if hasattr(resultado, 'registros'):
        # Es un objeto Pydantic con atributo registros
        regs = resultado.registros
        # Convertir cada registro a dict si es necesario
        return [r.model_dump() if hasattr(r, 'model_dump') else r for r in regs]
    elif hasattr(resultado, 'model_dump'):
        return resultado.model_dump().get("registros", [])
    elif isinstance(resultado, dict):
        return resultado.get("registros", [])
    return []


def _extract_campanas(resultado) -> List[Dict[str, Any]]:
    """Extrae campañas de un resultado que puede ser Pydantic o dict"""
    if hasattr(resultado, 'campanas'):
        regs = resultado.campanas
        return [r.model_dump() if hasattr(r, 'model_dump') else r for r in regs]
    elif hasattr(resultado, 'model_dump'):
        return resultado.model_dump().get("campanas", [])
    elif isinstance(resultado, dict):
        return resultado.get("campanas", [])
    return []


@router.get(
    "/pais_by_name/{name}",
    summary="Obtener recaudo por nombre de país/campaña",
    description="Endpoint compatible con FE - obtiene recaudo mensual por nombre de campaña"
)
async def obtener_recaudo_por_nombre(
    name: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2020, description="Año")
):
    """
    Obtiene el recaudo total de un país/campaña por nombre.
    Compatible con el FE existente.
    
    Retorna:
    - recaudo_total: Total recaudado en el mes
    - meta_total: Meta del mes
    - porcentaje_cumplimiento: % de cumplimiento
    - subcampanas: Lista de subcampañas con sus totales
    """
    try:
        # Buscar ID de campaña por nombre
        id_campana = _get_campana_id(name)
        
        if id_campana is None:
            # Intentar buscar en la BD
            campanas_result = CampanaService.obtener_todas()
            campanas = _extract_campanas(campanas_result)
            for c in campanas:
                if name.upper() in c.get("nombre", "").upper():
                    id_campana = c.get("id")
                    break
        
        if id_campana is None:
            return {
                "recaudo_total": 0,
                "meta_total": 0,
                "porcentaje_cumplimiento": 0,
                "total_pais": 0,
                "subcampanas": []
            }
        
        # Formatear periodo
        anio_mes = f"{anio}-{str(mes).zfill(2)}"
        
        # Obtener recaudo mensual
        resultado = RecaudoService.obtener_recaudo_mensual(
            id_campana=id_campana,
            anio_mes=anio_mes,
            solo_activos=True
        )
        
        # El servicio retorna un objeto Pydantic, convertir a dict
        registros = _extract_registros(resultado)
        
        # Calcular totales
        recaudo_total = 0
        meta_total = 0
        subcampanas = []
        
        for r in registros:
            rec = r.get("TotalRecaudoMes", 0) or 0
            met = r.get("TotalMetaMes", 0) or 0
            nombre = r.get("NombreInversionistaQA", "")
            porc = r.get("PorcentajeCumplimientoMes", 0)
            
            recaudo_total += float(rec)
            meta_total += float(met)
            
            subcampanas.append({
                "nombre_campana": nombre,
                "nombre": nombre,
                "total": float(rec),
                "recaudo_total": float(rec),
                "meta": float(met),
                "porcentaje": float(porc)
            })
        
        porcentaje = (recaudo_total / meta_total * 100) if meta_total > 0 else 0
        
        return {
            "recaudo_total": recaudo_total,
            "meta_total": meta_total,
            "porcentaje_cumplimiento": porcentaje,
            "total_pais": recaudo_total,
            "subcampanas": subcampanas
        }
        
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo por nombre: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/pais_by_name/{name}/diario",
    summary="Obtener recaudo diario por nombre de país/campaña",
    description="Endpoint compatible con FE - obtiene recaudo diario por nombre de campaña"
)
async def obtener_recaudo_diario_por_nombre(
    name: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2020, description="Año")
):
    """
    Obtiene el recaudo diario de un país/campaña por nombre.
    Compatible con el FE existente para gráficos.
    """
    try:
        id_campana = _get_campana_id(name)

        # Manejo especial: si es NPL PER, usar DAL tolerante a la vista Teseo
        name_upper = name.upper().strip()
        if "PER" in name_upper:
            # Llamar al DAL específico que normaliza la serie diaria
            try:
                data = portafolio_dal.obtener_recaudo_diario_teseo_peru(mes, anio)
                return data
            except Exception as e:
                logger.warning(f"Fallo consulta Teseo para {name}: {e}")

        if id_campana is None:
            campanas_result = CampanaService.obtener_todas()
            campanas = _extract_campanas(campanas_result)
            for c in campanas:
                if name.upper() in c.get("nombre", "").upper():
                    id_campana = c.get("id")
                    break
        
        if id_campana is None:
            return []
        
        anio_mes = f"{anio}-{str(mes).zfill(2)}"
        
        resultado = RecaudoService.obtener_recaudo_diario(
            id_campana=id_campana,
            anio_mes=anio_mes,
            solo_activos=True
        )
        
        registros = _extract_registros(resultado)
        
        # Transformar al formato esperado por el FE
        diario = []
        for r in registros:
            dia_habil = r.get("DiaHabil", 1)
            # Construir fecha
            fecha = f"{anio}-{str(mes).zfill(2)}-{str(dia_habil).zfill(2)}"
            diario.append({
                "fecha": fecha,
                "total": float(r.get("ValorRecaudoDia", 0) or 0),
                "meta_diaria": float(r.get("MetaDia", 0) or 0),
                "dia": dia_habil
            })
        
        return diario
        
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo diario: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return []


@router.get(
    "/pais/{id_pais}",
    summary="Obtener recaudo por ID de país/campaña",
    description="Endpoint compatible con FE - obtiene recaudo mensual por ID"
)
async def obtener_recaudo_por_id(
    id_pais: int,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2020, description="Año")
):
    """
    Obtiene el recaudo total de un país/campaña por ID.
    """
    try:
        anio_mes = f"{anio}-{str(mes).zfill(2)}"
        
        resultado = RecaudoService.obtener_recaudo_mensual(
            id_campana=id_pais,
            anio_mes=anio_mes,
            solo_activos=True
        )
        
        registros = _extract_registros(resultado)
        
        recaudo_total = 0
        meta_total = 0
        subcampanas = []
        
        for r in registros:
            rec = r.get("TotalRecaudoMes", 0) or 0
            met = r.get("TotalMetaMes", 0) or 0
            nombre = r.get("NombreInversionistaQA", "")
            porc = r.get("PorcentajeCumplimientoMes", 0)
            
            recaudo_total += float(rec)
            meta_total += float(met)
            
            subcampanas.append({
                "nombre_campana": nombre,
                "nombre": nombre,
                "total": float(rec),
                "recaudo_total": float(rec),
                "meta": float(met),
                "porcentaje": float(porc)
            })
        
        porcentaje = (recaudo_total / meta_total * 100) if meta_total > 0 else 0
        
        return {
            "recaudo_total": recaudo_total,
            "meta_total": meta_total,
            "porcentaje_cumplimiento": porcentaje,
            "total_pais": recaudo_total,
            "subcampanas": subcampanas
        }
        
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo por ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/pais/{id_pais}/diario",
    summary="Obtener recaudo diario por ID de país/campaña",
    description="Endpoint compatible con FE - obtiene recaudo diario por ID"
)
async def obtener_recaudo_diario_por_id(
    id_pais: int,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2020, description="Año")
):
    """
    Obtiene el recaudo diario de un país/campaña por ID.
    """
    try:
        anio_mes = f"{anio}-{str(mes).zfill(2)}"
        
        resultado = RecaudoService.obtener_recaudo_diario(
            id_campana=id_pais,
            anio_mes=anio_mes,
            solo_activos=True
        )
        
        registros = _extract_registros(resultado)
        
        diario = []
        for r in registros:
            dia_habil = r.get("DiaHabil", 1)
            fecha = f"{anio}-{str(mes).zfill(2)}-{str(dia_habil).zfill(2)}"
            diario.append({
                "fecha": fecha,
                "total": float(r.get("ValorRecaudoDia", 0) or 0),
                "meta_diaria": float(r.get("MetaDia", 0) or 0),
                "dia": dia_habil
            })
        
        return diario
        
    except DatabaseError as e:
        logger.error(f"Error al obtener recaudo diario por ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return []


@router.get(
    "/campana/{nombre}",
    summary="Obtener recaudo por nombre de campaña",
    description="Endpoint compatible con FE - alias de pais_by_name"
)
async def obtener_recaudo_por_campana(
    nombre: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2020, description="Año")
):
    """
    Alias de /pais_by_name para compatibilidad con el FE.
    """
    return await obtener_recaudo_por_nombre(nombre, mes, anio)
