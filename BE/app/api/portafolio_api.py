"""
API para datos de recaudo desde vw_recaudos_portafolio.
Endpoints para acceder a datos de campañas pequeñas de Colombia desde la BD.
"""

from fastapi import APIRouter, Query, HTTPException
from app.dal.portafolio_dal import (
    obtener_recaudo_campana_portafolio,
    obtener_recaudo_diario_portafolio,
    obtener_campanas_disponibles_portafolio,
    obtener_total_pais_portafolio,
    obtener_subcampanas_pais_portafolio,
    verificar_conexion_portafolio,
    obtener_resumen_mensual_portafolio,
    obtener_recaudo_tanque_sin_identificar,
    obtener_recaudo_tanque_pais,
)
from datetime import datetime

router = APIRouter(prefix="/portafolio", tags=["Portafolio - BD vw_recaudos_portafolio"])


@router.get("/health")
def verificar_conexion():
    """
    Verifica que la conexión a la BD de portafolio esté funcionando.
    """
    try:
        conexion_ok = verificar_conexion_portafolio()
        return {
            "status": "ok" if conexion_ok else "error",
            "mensaje": "Conexión a vw_recaudos_portafolio exitosa" if conexion_ok else "No se pudo conectar",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campanas")
def listar_campanas_disponibles(
    mes: int = Query(None, ge=1, le=12, description="Filtrar por mes específico")
):
    """
    Lista todas las campañas disponibles en la vista vw_recaudos_portafolio.
    """
    try:
        campanas = obtener_campanas_disponibles_portafolio(mes)
        return {
            "campanas": campanas,
            "total": len(campanas),
            "mes_filtro": mes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recaudo/campana/{nombre_campana}")
def obtener_recaudo_campana(
    nombre_campana: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(2025, ge=2000, description="Año"),
    hasta_dia: int = Query(None, ge=1, le=31, description="Día límite (para 'hasta hoy')")
):
    """
    Obtiene el recaudo total de una campaña específica desde la BD.
    
    Campañas disponibles:
    - SYSTEMGROUP CREDIVALORES NPL
    - SYSTEMGROUP ACCION FIDUCIARIA- DENTIX
    - SYSTEMGROUP ADAMANTINE - COLPATRIA NPL
    - SYSTEMGROUP JCAP
    - SYSTEMGROUP PRA GROUP
    - SYSTEMGROUP COLOMBIA (total general)
    """
    try:
        result = obtener_recaudo_campana_portafolio(nombre_campana, mes, anio, hasta_dia)
        return {
            "nombre_campana": nombre_campana,
            "mes": mes,
            "anio": anio,
            "hasta_dia": hasta_dia,
            "total": result["total"],
            "cantidad": result["cantidad"],
            "fuente": "BD"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recaudo/campana/{nombre_campana}/diario")
def obtener_recaudo_diario_campana(
    nombre_campana: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(2025, ge=2000, description="Año")
):
    """
    Obtiene el recaudo diario de una campaña desde la BD.
    Útil para gráficos de evolución diaria.
    """
    try:
        result = obtener_recaudo_diario_portafolio(nombre_campana, mes, anio)
        return {
            "nombre_campana": nombre_campana,
            "mes": mes,
            "anio": anio,
            "dias": result,
            "total_dias": len(result),
            "fuente": "BD"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recaudo/pais/{pais}")
def obtener_recaudo_pais(
    pais: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(2025, ge=2000, description="Año"),
    hasta_dia: int = Query(None, ge=1, le=31, description="Día límite")
):
    """
    Obtiene el recaudo total de un país (NPL, ACC) desde la BD.
    """
    try:
        result = obtener_total_pais_portafolio(pais, mes, anio, hasta_dia)
        return {
            "pais": pais,
            "mes": mes,
            "anio": anio,
            "hasta_dia": hasta_dia,
            "total": result["total"],
            "cantidad": result["cantidad"],
            "fuente": "BD"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recaudo/pais/{pais}/subcampanas")
def obtener_subcampanas_pais(
    pais: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(2025, ge=2000, description="Año")
):
    """
    Obtiene el desglose de subcampañas de un país desde la BD.
    Indica qué campañas tienen datos en BD y cuáles deben buscarse en Excel.
    """
    try:
        result = obtener_subcampanas_pais_portafolio(pais, mes, anio)
        
        # Calcular totales
        total_bd = sum(s["total"] for s in result if s.get("fuente") == "BD")
        total_excel = sum(s["total"] for s in result if s.get("fuente") == "EXCEL")
        
        return {
            "pais": pais,
            "mes": mes,
            "anio": anio,
            "subcampanas": result,
            "resumen": {
                "total_campanas": len(result),
                "campanas_en_bd": len([s for s in result if s.get("fuente") == "BD"]),
                "campanas_en_excel": len([s for s in result if s.get("fuente") == "EXCEL"]),
                "total_bd": total_bd,
                "total_excel": total_excel
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resumen/mensual")
def obtener_resumen_mensual(
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(2025, ge=2000, description="Año")
):
    """
    Obtiene un resumen de recaudo mensual por todas las campañas en la BD.
    """
    try:
        result = obtener_resumen_mensual_portafolio(mes, anio)
        total_general = sum(r["total_mes"] for r in result)
        
        return {
            "mes": mes,
            "anio": anio,
            "campanas": result,
            "total_campanas": len(result),
            "total_general": total_general,
            "fuente": "BD"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mapeo/campanas")
def obtener_mapeo_campanas():
    """
    Devuelve el mapeo de campañas del FE a nombres en la BD.
    Útil para debugging y para el FE saber qué datos están en BD.
    """
    from app.database import CAMPANAS_PEQUENAS_BD_MAPPING
    
    return {
        "mapeo": CAMPANAS_PEQUENAS_BD_MAPPING,
        "descripcion": {
            "NPL": "Campañas NPL Colombia",
            "ACC": "Campañas ACC (Acción, Adamantine, JCAP, PRA Group)",
            "SYSTEMGROUP COLOMBIA": "Alias para ACC"
        },
        "campanas_disponibles_bd": [
            "SYSTEMGROUP CREDIVALORES NPL",
            "SYSTEMGROUP ACCION FIDUCIARIA- DENTIX",
            "SYSTEMGROUP ADAMANTINE - COLPATRIA NPL",
            "SYSTEMGROUP JCAP",
            "SYSTEMGROUP PRA GROUP",
            "SYSTEMGROUP COLOMBIA"
        ]
    }


@router.get("/tanque/campana/{nombre_campana}")
def obtener_tanque_campana(
    nombre_campana: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(2026, ge=2000, description="Año"),
    hasta_dia: int = Query(None, ge=1, le=31, description="Día límite (para 'hasta hoy')")
):
    """
    Obtiene el recaudo sin identificar (tanque) de una campaña específica.
    
    Returns:
        Dict con total y cantidad de recaudos sin identificar
    """
    try:
        result = obtener_recaudo_tanque_sin_identificar(nombre_campana, mes, anio, hasta_dia)
        return {
            "nombre_campana": nombre_campana,
            "mes": mes,
            "anio": anio,
            "hasta_dia": hasta_dia,
            "total": result["total"],
            "cantidad": result["cantidad"],
            "fuente": "BD - Tanque sin identificar"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tanque/pais/{pais}")
def obtener_tanque_pais(
    pais: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(2026, ge=2000, description="Año"),
    hasta_dia: int = Query(None, ge=1, le=31, description="Día límite")
):
    """
    Obtiene el recaudo sin identificar (tanque) total de un país.
    
    Args:
        pais: NPL COL, ACC, CHILE, etc.
    """
    try:
        result = obtener_recaudo_tanque_pais(pais, mes, anio, hasta_dia)
        return {
            "pais": pais,
            "mes": mes,
            "anio": anio,
            "hasta_dia": hasta_dia,
            "total": result["total"],
            "cantidad": result["cantidad"],
            "fuente": "BD - Tanque sin identificar"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
