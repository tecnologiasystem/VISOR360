from app.dal.recaudo_dal import (
    obtener_todos_los_recaudos,
    obtener_recaudo_filtrado,
    obtener_recaudos_por_pais_con_subcampanas,
    obtener_recaudo_diario_pais,
)


def listar_recaudos():
    """
    Esta función representa la lógica de negocio.
    Puede aplicar reglas, filtros, cálculos, etc.
    Por ahora solo pasa los datos del DAL hacia la API.
    """
    recaudos = obtener_todos_los_recaudos()
    return recaudos


def obtener_recaudo_por_campana_mes(
    nombre_campana: str, mes: int, anio: int, hasta_hoy: bool = False
):
    """
    Obtiene el recaudo total de una campaña en un mes específico usando el nombre de la campaña.
    Si hasta_hoy=True, solo suma recaudos hasta el día actual.
    """
    resultado = obtener_recaudo_filtrado(nombre_campana, mes, anio, hasta_hoy)
    return {
        "nombre_campana": nombre_campana,
        "mes": mes,
        "anio": anio,
        "recaudo_total": resultado["total"],
        "cantidad_recaudos": resultado["cantidad"],
    }


def obtener_recaudo_pais_completo(pais_param, mes: int, anio: int):
    """
    Obtiene el recaudo de un país con el desglose por subcampañas.
    Puede recibir id_pais (int) o nombre_pais (str).
    """
    return obtener_recaudos_por_pais_con_subcampanas(pais_param, mes, anio)


def obtener_recaudo_diario(id_pais: int, mes: int, anio: int):
    """
    Obtiene el recaudo agrupado por día de un país en un mes.
    """
    return obtener_recaudo_diario_pais(id_pais, mes, anio)
