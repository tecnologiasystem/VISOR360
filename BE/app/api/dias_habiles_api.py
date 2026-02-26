"""
API para días hábiles y comparación de recaudos por día hábil.
Permite comparar el recaudo del día hábil N del mes actual con el día hábil N de otro mes.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import date
from app.utils.dias_habiles import (
    obtener_dias_habiles_mes,
    obtener_dia_habil_actual,
    obtener_fecha_por_dia_habil,
    comparar_dias_habiles,
    obtener_festivos_colombia,
    obtener_info_dia_habil_actual,
    obtener_total_dias_habiles_mes,
)
from app.dal.portafolio_dal import obtener_recaudo_campana_portafolio
from app.dal.recaudo_dal import obtener_total_excel_hasta_dia_habil
from app.database import get_campana_bd_name, CAMPANAS_PEQUENAS

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dias-habiles", tags=["Días Hábiles"])


@router.get("/info-hoy")
def get_info_dia_habil_actual(
    id_campana: Optional[int] = Query(None, description="ID de campaña para configuración específica")
):
    """
    Retorna información del día hábil actual.
    Útil para el frontend para mostrar "Día hábil 8 de 20".
    Si se proporciona id_campana, aplica la configuración específica de la BD.
    """
    from datetime import date as dt_date
    
    info_base = obtener_info_dia_habil_actual()
    
    # Si hay id_campana, recalcular con configuración de BD
    if id_campana is not None:
        try:
            from app.bll.campana_configuracion_bll import CampanaConfiguracionBLL
            import calendar
            
            hoy = dt_date.today()
            anio = hoy.year
            mes = hoy.month
            
            start_date = dt_date(anio, mes, 1)
            last_day = calendar.monthrange(anio, mes)[1]
            end_date = dt_date(anio, mes, last_day)
            
            # Obtener configuración de BD
            config_bd = CampanaConfiguracionBLL.obtener_configuracion(id_campana, start_date, end_date)
            
            # Crear mapa de fecha -> es_habil (False = NO hábil por config BD)
            fechas_no_habiles = set()
            for item in config_bd:
                if not item["EsHabil"]:
                    fecha = item["Fecha"]
                    if hasattr(fecha, "isoformat"):
                        fechas_no_habiles.add(fecha.isoformat())
                    else:
                        fechas_no_habiles.add(str(fecha))
            
            # Recalcular días hábiles del mes considerando BD
            dias_habiles = obtener_dias_habiles_mes(anio, mes)
            
            # Filtrar días que están marcados como NO hábiles en BD
            dias_filtrados = [d for d in dias_habiles if d["fecha"] not in fechas_no_habiles]
            
            # Calcular día hábil actual
            hoy_str = hoy.isoformat()
            dia_habil_actual = 0
            for d in dias_filtrados:
                if d["fecha"] <= hoy_str:
                    dia_habil_actual += 1
            
            return {
                **info_base,
                "dia_habil": dia_habil_actual,
                "dia_habil_actual": dia_habil_actual,
                "total_dias_habiles_mes": len(dias_filtrados),
                "dias_habiles_restantes": len([d for d in dias_filtrados if d["fecha"] > hoy_str]),
                "configuracion_aplicada": True
            }
            
        except Exception as e:
            logger.warning(f"Error aplicando config de campaña {id_campana} en info-hoy: {e}")
            # Continuar con info base si falla
    
    return info_base


@router.get("/mes/{anio}/{mes}")
def get_dias_habiles_mes(
    anio: int,
    mes: int,
    id_campana: Optional[int] = Query(None, description="ID de campaña para configuración específica")
):
    """
    Retorna la lista de días hábiles de un mes con su número de día hábil.
    Si se proporciona id_campana, aplica la configuración específica de la BD.
    """
    if mes < 1 or mes > 12:
        raise HTTPException(status_code=400, detail="Mes debe estar entre 1 y 12")
    
    # Obtener días hábiles base (festivos Colombia)
    dias = obtener_dias_habiles_mes(anio, mes)
    
    # Si hay id_campana, aplicar configuración específica de BD
    if id_campana is not None:
        try:
            from app.bll.campana_configuracion_bll import CampanaConfiguracionBLL
            from datetime import date as dt_date
            
            start_date = dt_date(anio, mes, 1)
            if mes == 12:
                end_date = dt_date(anio, 12, 31)
            else:
                import calendar
                last_day = calendar.monthrange(anio, mes)[1]
                end_date = dt_date(anio, mes, last_day)
            
            # Obtener configuración de BD
            config_bd = CampanaConfiguracionBLL.obtener_configuracion(id_campana, start_date, end_date)
            
            # Crear mapa de fecha -> es_habil
            config_map = {}
            for item in config_bd:
                fecha = item["Fecha"]
                if hasattr(fecha, "isoformat"):
                    fecha_str = fecha.isoformat()
                else:
                    fecha_str = str(fecha)
                config_map[fecha_str] = item["EsHabil"]
            
            # Aplicar configuración a los días
            dias_filtrados = []
            num_dia_habil = 0
            
            for dia in dias:
                fecha_str = dia["fecha"]
                # Si la fecha está en config_map, usar ese valor
                if fecha_str in config_map:
                    es_habil_bd = config_map[fecha_str]
                    if es_habil_bd:
                        num_dia_habil += 1
                        dias_filtrados.append({
                            **dia,
                            "dia_habil": num_dia_habil
                        })
                    # Si es_habil_bd es False, NO agregar el día
                else:
                    # No está en config, mantener como viene (hábil por defecto)
                    num_dia_habil += 1
                    dias_filtrados.append({
                        **dia,
                        "dia_habil": num_dia_habil
                    })
            
            dias = dias_filtrados
            
        except Exception as e:
            logger.warning(f"Error aplicando config de campaña {id_campana}: {e}")
            # Continuar con días base si falla
    
    return {
        "anio": anio,
        "mes": mes,
        "total_dias_habiles": len(dias),
        "dias": dias
    }



@router.get("/festivos/{anio}")
def get_festivos_anio(anio: int):
    """
    Retorna la lista de festivos de Colombia para un año.
    """
    festivos = obtener_festivos_colombia(anio)
    return {
        "anio": anio,
        "festivos": [
            {
                "fecha": f.isoformat(),
                "dia": f.day,
                "mes": f.month,
                "dia_semana": f.strftime("%A")
            }
            for f in festivos
        ]
    }


@router.get("/comparar")
def comparar_meses(
    mes_actual: int = Query(..., ge=1, le=12),
    anio_actual: int = Query(..., ge=2020),
    mes_comparar: int = Query(..., ge=1, le=12),
    anio_comparar: int = Query(..., ge=2020),
    hasta_dia_habil: Optional[int] = Query(None, ge=1, description="Día hábil hasta el cual comparar")
):
    """
    Compara dos meses y retorna el mapeo de días hábiles.
    Si no se especifica hasta_dia_habil, usa el día hábil actual.
    """
    return comparar_dias_habiles(
        anio_actual, mes_actual,
        anio_comparar, mes_comparar,
        hasta_dia_habil
    )


@router.get("/recaudo-comparativo/{pais}")
def get_recaudo_comparativo_dia_habil(
    pais: str,
    mes_actual: int = Query(..., ge=1, le=12),
    anio_actual: int = Query(..., ge=2020),
    mes_comparar: int = Query(..., ge=1, le=12),
    anio_comparar: int = Query(..., ge=2020),
    hasta_dia_habil: Optional[int] = Query(None, ge=1, description="Día hábil hasta el cual comparar")
):
    """
    Compara el recaudo acumulado hasta un día hábil específico entre dos meses.
    
    Por ejemplo: Comparar el recaudo hasta el día hábil 8 de diciembre 2025
    con el recaudo hasta el día hábil 8 de noviembre 2025.
    
    Args:
        pais: Nombre del país/campaña (ej: "NPL COL", "ACC")
        mes_actual: Mes actual a analizar
        anio_actual: Año actual
        mes_comparar: Mes de comparación
        anio_comparar: Año de comparación
        hasta_dia_habil: Día hábil hasta el cual comparar (default: día hábil actual)
    """
    try:
        # Obtener comparación de días hábiles
        comparacion = comparar_dias_habiles(
            anio_actual, mes_actual,
            anio_comparar, mes_comparar,
            hasta_dia_habil
        )
        
        dia_habil = comparacion["dia_habil"]
        
        # Obtener el día calendario equivalente para cada mes
        dia_actual = comparacion["mes_actual"]["dia_mes"]
        dia_comparar = comparacion["mes_comparar"]["dia_mes"]
        
        # Obtener subcampañas del país
        pais_upper = pais.upper().strip()
        subcampanas = CAMPANAS_PEQUENAS.get(pais_upper, [])
        
        if not subcampanas:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron subcampañas para el país: {pais}"
            )
        
        resultado_actual = {"total": 0.0, "por_campana": {}}
        resultado_comparar = {"total": 0.0, "por_campana": {}}
        
        for subcampana in subcampanas:
            nombre_bd = get_campana_bd_name(pais_upper, subcampana)
            
            if nombre_bd:
                # Primero intentar obtener desde BD (día calendario equivalente)
                try:
                    rec_actual = obtener_recaudo_campana_portafolio(
                        nombre_bd, mes_actual, anio_actual,
                        hasta_dia=dia_actual
                    )
                except Exception:
                    rec_actual = {"total": 0.0, "cantidad": 0}

                # Si BD no tiene datos (0), fallback a Excel usando día hábil
                if not rec_actual or rec_actual.get("total", 0) == 0:
                    try:
                        rec_excel_actual = obtener_total_excel_hasta_dia_habil(
                            pais, subcampana, mes_actual, anio_actual, dia_habil
                        )
                        rec_actual = {"total": rec_excel_actual.get("total", 0.0), "cantidad": rec_excel_actual.get("cantidad", 0)}
                    except Exception:
                        rec_actual = {"total": 0.0, "cantidad": 0}

                resultado_actual["total"] += rec_actual["total"]
                resultado_actual["por_campana"][subcampana] = rec_actual["total"]

                # Mes comparar
                try:
                    rec_comparar = obtener_recaudo_campana_portafolio(
                        nombre_bd, mes_comparar, anio_comparar,
                        hasta_dia=dia_comparar
                    )
                except Exception:
                    rec_comparar = {"total": 0.0, "cantidad": 0}

                if not rec_comparar or rec_comparar.get("total", 0) == 0:
                    try:
                        rec_excel_comparar = obtener_total_excel_hasta_dia_habil(
                            pais, subcampana, mes_comparar, anio_comparar, dia_habil
                        )
                        rec_comparar = {"total": rec_excel_comparar.get("total", 0.0), "cantidad": rec_excel_comparar.get("cantidad", 0)}
                    except Exception:
                        rec_comparar = {"total": 0.0, "cantidad": 0}

                resultado_comparar["total"] += rec_comparar["total"]
                resultado_comparar["por_campana"][subcampana] = rec_comparar["total"]
            else:
                # No hay mapeo BD: usar Excel directamente (filtrando por día hábil)
                try:
                    rec_excel_actual = obtener_total_excel_hasta_dia_habil(pais, subcampana, mes_actual, anio_actual, dia_habil)
                except Exception:
                    rec_excel_actual = {"total": 0.0, "cantidad": 0}

                try:
                    rec_excel_comparar = obtener_total_excel_hasta_dia_habil(pais, subcampana, mes_comparar, anio_comparar, dia_habil)
                except Exception:
                    rec_excel_comparar = {"total": 0.0, "cantidad": 0}

                resultado_actual["total"] += rec_excel_actual.get("total", 0.0)
                resultado_actual["por_campana"][subcampana] = rec_excel_actual.get("total", 0.0)
                resultado_comparar["total"] += rec_excel_comparar.get("total", 0.0)
                resultado_comparar["por_campana"][subcampana] = rec_excel_comparar.get("total", 0.0)
        
        # Calcular variación
        variacion = 0
        if resultado_comparar["total"] > 0:
            variacion = (resultado_actual["total"] - resultado_comparar["total"]) / resultado_comparar["total"]
        
        return {
            "pais": pais,
            "dia_habil": dia_habil,
            "mes_actual": {
                "mes": mes_actual,
                "anio": anio_actual,
                "fecha_corte": comparacion["mes_actual"]["fecha"],
                "dia_calendario": dia_actual,
                "total_recaudo": resultado_actual["total"],
                "por_campana": resultado_actual["por_campana"],
                "total_dias_habiles_mes": comparacion["mes_actual"]["total_dias_habiles"]
            },
            "mes_comparar": {
                "mes": mes_comparar,
                "anio": anio_comparar,
                "fecha_corte": comparacion["mes_comparar"]["fecha"],
                "dia_calendario": dia_comparar,
                "total_recaudo": resultado_comparar["total"],
                "por_campana": resultado_comparar["por_campana"],
                "total_dias_habiles_mes": comparacion["mes_comparar"]["total_dias_habiles"]
            },
            "variacion_porcentaje": variacion,
            "variacion_absoluta": resultado_actual["total"] - resultado_comparar["total"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en recaudo comparativo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recaudo-diario-habil/{pais}")
def get_recaudo_por_dia_habil(
    pais: str,
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2020),
):
    """
    Retorna el recaudo día a día pero usando días hábiles en lugar de días calendario.
    Cada registro indica: día hábil N, fecha, recaudo de ese día.
    
    Útil para comparar gráficamente días hábiles entre meses.
    """
    try:
        # Obtener días hábiles del mes
        dias_habiles = obtener_dias_habiles_mes(anio, mes)
        
        # Obtener subcampañas del país
        pais_upper = pais.upper().strip()
        subcampanas = CAMPANAS_PEQUENAS.get(pais_upper, [])
        
        if not subcampanas:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron subcampañas para el país: {pais}"
            )
        
        # Para cada día hábil, obtener el recaudo acumulado
        resultado = []
        recaudo_acumulado = 0.0
        
        for dia_info in dias_habiles:
            dia_calendario = dia_info["dia_mes"]
            dia_habil = dia_info["dia_habil"]
            fecha = dia_info["fecha"]

            # Obtener recaudo del día para todas las subcampañas
            recaudo_dia = 0.0
            for subcampana in subcampanas:
                nombre_bd = get_campana_bd_name(pais_upper, subcampana)
                if nombre_bd:
                    # Intentar BD primero (día calendario)
                    try:
                        rec = obtener_recaudo_campana_portafolio(
                            nombre_bd, mes, anio,
                            hasta_dia=dia_calendario
                        )
                    except Exception:
                        rec = {"total": 0.0, "cantidad": 0}

                    if dia_habil == 1:
                        acumulado_actual = rec.get("total", 0.0)
                        acumulado_prev = 0.0
                    else:
                        try:
                            rec_anterior = obtener_recaudo_campana_portafolio(
                                nombre_bd, mes, anio,
                                hasta_dia=dia_calendario - 1
                            )
                            acumulado_actual = rec.get("total", 0.0)
                            acumulado_prev = rec_anterior.get("total", 0.0)
                        except Exception:
                            acumulado_actual = rec.get("total", 0.0)
                            acumulado_prev = 0.0

                    # Si BD no muestra datos (0), fallback a Excel filtrando por día hábil
                    if (acumulado_actual == 0 and acumulado_prev == 0):
                        try:
                            excel_actual = obtener_total_excel_hasta_dia_habil(pais, subcampana, mes, anio, dia_habil)
                            excel_prev = obtener_total_excel_hasta_dia_habil(pais, subcampana, mes, anio, max(1, dia_habil - 1)) if dia_habil > 1 else {"total": 0.0, "cantidad": 0}
                            recaudo_dia += excel_actual.get("total", 0.0) - excel_prev.get("total", 0.0)
                        except Exception:
                            # no data, add 0
                            recaudo_dia += 0.0
                    else:
                        recaudo_dia += max(0.0, acumulado_actual - acumulado_prev)
                else:
                    # No hay mapeo BD: usar Excel directo (filtrar por dia hábil)
                    try:
                        excel_actual = obtener_total_excel_hasta_dia_habil(pais, subcampana, mes, anio, dia_habil)
                        excel_prev = obtener_total_excel_hasta_dia_habil(pais, subcampana, mes, anio, max(1, dia_habil - 1)) if dia_habil > 1 else {"total": 0.0, "cantidad": 0}
                        recaudo_dia += excel_actual.get("total", 0.0) - excel_prev.get("total", 0.0)
                    except Exception:
                        recaudo_dia += 0.0

            recaudo_acumulado += recaudo_dia

            resultado.append({
                "dia_habil": dia_habil,
                "dia_calendario": dia_calendario,
                "fecha": fecha,
                "recaudo_dia": recaudo_dia,
                "recaudo_acumulado": recaudo_acumulado,
                "es_hoy": dia_info.get("es_hoy", False)
            })
        
        return {
            "pais": pais,
            "mes": mes,
            "anio": anio,
            "total_dias_habiles": len(dias_habiles),
            "recaudo_total": recaudo_acumulado,
            "dias": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo recaudo por día hábil: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recaudo-comparativo-detallado/{pais}")
def get_recaudo_comparativo_detallado(
    pais: str,
    mes_actual: int = Query(..., ge=1, le=12),
    anio_actual: int = Query(..., ge=2020),
    mes_comparar: int = Query(..., ge=1, le=12),
    anio_comparar: int = Query(..., ge=2020),
):
    """
    Retorna el recaudo acumulado por día hábil de ambos meses para graficar.
    Permite ver la curva de recaudo día a día hábil.
    """
    try:
        # Obtener días hábiles de ambos meses
        dias_actual = obtener_dias_habiles_mes(anio_actual, mes_actual)
        dias_comparar = obtener_dias_habiles_mes(anio_comparar, mes_comparar)
        
        pais_upper = pais.upper().strip()
        subcampanas = CAMPANAS_PEQUENAS.get(pais_upper, [])
        
        if not subcampanas:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron subcampañas para el país: {pais}"
            )
        
        # Función helper para obtener recaudo acumulado hasta un día
        def get_recaudo_hasta_dia(mes: int, anio: int, dia_calendario: int, dia_habil: int) -> float:
            total = 0.0
            for subcampana in subcampanas:
                nombre_bd = get_campana_bd_name(pais_upper, subcampana)
                if nombre_bd:
                    try:
                        rec = obtener_recaudo_campana_portafolio(
                            nombre_bd, mes, anio, hasta_dia=dia_calendario
                        )
                    except Exception:
                        rec = {"total": 0.0, "cantidad": 0}

                    if rec.get("total", 0.0) > 0:
                        total += rec.get("total", 0.0)
                    else:
                        # Fallback a Excel (filtrar por día hábil)
                        try:
                            rec_excel = obtener_total_excel_hasta_dia_habil(pais, subcampana, mes, anio, dia_habil)
                            total += rec_excel.get("total", 0.0)
                        except Exception:
                            total += 0.0
                else:
                    try:
                        rec_excel = obtener_total_excel_hasta_dia_habil(pais, subcampana, mes, anio, dia_habil)
                        total += rec_excel.get("total", 0.0)
                    except Exception:
                        total += 0.0
            return total
        
        # Construir series para ambos meses
        serie_actual = []
        serie_comparar = []
        
        max_dias = max(len(dias_actual), len(dias_comparar))
        
        for i in range(max_dias):
            dia_habil = i + 1
            
            # Mes actual
            if i < len(dias_actual):
                dia_info = dias_actual[i]
                rec = get_recaudo_hasta_dia(mes_actual, anio_actual, dia_info["dia_mes"], dia_habil)
                serie_actual.append({
                    "dia_habil": dia_habil,
                    "fecha": dia_info["fecha"],
                    "dia_calendario": dia_info["dia_mes"],
                    "recaudo_acumulado": rec
                })
            
            # Mes a comparar
            if i < len(dias_comparar):
                dia_info = dias_comparar[i]
                rec = get_recaudo_hasta_dia(mes_comparar, anio_comparar, dia_info["dia_mes"], dia_habil)
                serie_comparar.append({
                    "dia_habil": dia_habil,
                    "fecha": dia_info["fecha"],
                    "dia_calendario": dia_info["dia_mes"],
                    "recaudo_acumulado": rec
                })
        
        # Día hábil actual
        dia_habil_actual = obtener_dia_habil_actual(anio_actual, mes_actual)
        
        return {
            "pais": pais,
            "dia_habil_actual": dia_habil_actual,
            "mes_actual": {
                "mes": mes_actual,
                "anio": anio_actual,
                "total_dias_habiles": len(dias_actual),
                "serie": serie_actual
            },
            "mes_comparar": {
                "mes": mes_comparar,
                "anio": anio_comparar,
                "total_dias_habiles": len(dias_comparar),
                "serie": serie_comparar
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en comparativo detallado: {e}")
        raise HTTPException(status_code=500, detail=str(e))
