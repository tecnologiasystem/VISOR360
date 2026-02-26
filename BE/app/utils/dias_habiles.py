"""
Módulo para el cálculo de días hábiles en Colombia.
Excluye fines de semana (sábado, domingo) y festivos colombianos.

Los festivos en Colombia son:
1. Fijos: Año Nuevo (1 Ene), Día del Trabajo (1 May), Independencia (20 Jul), 
         Batalla de Boyacá (7 Ago), Inmaculada Concepción (8 Dic), Navidad (25 Dic)
2. Móviles (Ley Emiliani - se pasan al lunes siguiente):
   - Reyes Magos (6 Ene → lunes)
   - San José (19 Mar → lunes)
   - Ascensión del Señor (39 días después de Pascua → lunes)
   - Corpus Christi (60 días después de Pascua → lunes)
   - Sagrado Corazón (68 días después de Pascua → lunes)
   - San Pedro y San Pablo (29 Jun → lunes)
   - Asunción de la Virgen (15 Ago → lunes)
   - Día de la Raza (12 Oct → lunes)
   - Todos los Santos (1 Nov → lunes)
   - Independencia de Cartagena (11 Nov → lunes)
3. Semana Santa: Jueves y Viernes Santo (calculados según Pascua)
"""

from datetime import date, timedelta
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def calcular_pascua(anio: int) -> date:
    """
    Calcula la fecha de Pascua (Domingo de Resurrección) usando el algoritmo de Butcher.
    """
    a = anio % 19
    b = anio // 100
    c = anio % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(anio, mes, dia)


def siguiente_lunes(fecha: date) -> date:
    """
    Si la fecha no es lunes, devuelve el siguiente lunes (Ley Emiliani).
    """
    dia_semana = fecha.weekday()  # 0 = Lunes
    if dia_semana == 0:
        return fecha
    dias_hasta_lunes = 7 - dia_semana
    return fecha + timedelta(days=dias_hasta_lunes)


def obtener_festivos_colombia(anio: int) -> List[date]:
    """
    Retorna la lista de todos los días festivos en Colombia para un año dado.
    """
    festivos = []
    
    # Festivos fijos
    festivos.append(date(anio, 1, 1))    # Año Nuevo
    festivos.append(date(anio, 5, 1))    # Día del Trabajo
    festivos.append(date(anio, 7, 20))   # Independencia de Colombia
    festivos.append(date(anio, 8, 7))    # Batalla de Boyacá
    festivos.append(date(anio, 12, 8))   # Inmaculada Concepción
    festivos.append(date(anio, 12, 25))  # Navidad
    
    # Festivos móviles (Ley Emiliani - al lunes siguiente)
    festivos.append(siguiente_lunes(date(anio, 1, 6)))    # Reyes Magos
    festivos.append(siguiente_lunes(date(anio, 3, 19)))   # San José
    festivos.append(siguiente_lunes(date(anio, 6, 29)))   # San Pedro y San Pablo
    festivos.append(siguiente_lunes(date(anio, 8, 15)))   # Asunción de la Virgen
    festivos.append(siguiente_lunes(date(anio, 10, 12)))  # Día de la Raza
    festivos.append(siguiente_lunes(date(anio, 11, 1)))   # Todos los Santos
    festivos.append(siguiente_lunes(date(anio, 11, 11)))  # Independencia de Cartagena
    
    # Festivos basados en Pascua
    pascua = calcular_pascua(anio)
    
    # Semana Santa
    jueves_santo = pascua - timedelta(days=3)
    viernes_santo = pascua - timedelta(days=2)
    festivos.append(jueves_santo)
    festivos.append(viernes_santo)
    
    # Festivos móviles basados en Pascua (Ley Emiliani)
    ascension = pascua + timedelta(days=39)
    festivos.append(siguiente_lunes(ascension))  # Ascensión del Señor
    
    corpus_christi = pascua + timedelta(days=60)
    festivos.append(siguiente_lunes(corpus_christi))  # Corpus Christi
    
    sagrado_corazon = pascua + timedelta(days=68)
    festivos.append(siguiente_lunes(sagrado_corazon))  # Sagrado Corazón
    
    return sorted(festivos)


def es_dia_habil(fecha: date, festivos: List[date] = None) -> bool:
    """
    Verifica si una fecha es día hábil en Colombia.
    Día hábil = No es sábado, ni domingo, ni festivo.
    """
    # Sábado = 5, Domingo = 6
    if fecha.weekday() >= 5:
        return False
    
    # Verificar festivos
    if festivos is None:
        festivos = obtener_festivos_colombia(fecha.year)
    
    return fecha not in festivos


def obtener_dias_habiles_mes(anio: int, mes: int) -> List[Dict]:
    """
    Retorna la lista de días hábiles de un mes con su número de día hábil.
    
    Returns:
        Lista de dicts con: {fecha, dia_mes, dia_habil, es_hoy}
    """
    from datetime import date as dt_date
    hoy = dt_date.today()
    
    festivos = obtener_festivos_colombia(anio)
    
    # Determinar primer y último día del mes
    primer_dia = date(anio, mes, 1)
    if mes == 12:
        ultimo_dia = date(anio + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(anio, mes + 1, 1) - timedelta(days=1)
    
    dias_habiles = []
    numero_dia_habil = 0
    
    dia_actual = primer_dia
    while dia_actual <= ultimo_dia:
        if es_dia_habil(dia_actual, festivos):
            numero_dia_habil += 1
            dias_habiles.append({
                "fecha": dia_actual.isoformat(),
                "dia_mes": dia_actual.day,
                "dia_habil": numero_dia_habil,
                "es_hoy": dia_actual == hoy,
                "es_festivo": False
            })
        dia_actual += timedelta(days=1)
    
    return dias_habiles


def obtener_dia_habil_actual(anio: int, mes: int) -> int:
    """
    Retorna el número de día hábil correspondiente a la fecha actual.
    Si el día actual no es hábil, retorna el último día hábil transcurrido.
    """
    from datetime import date as dt_date
    hoy = dt_date.today()
    
    # Verificar que estamos en el mes correcto
    if hoy.year != anio or hoy.month != mes:
        # Si el mes ya pasó, retornar el último día hábil del mes
        dias = obtener_dias_habiles_mes(anio, mes)
        return dias[-1]["dia_habil"] if dias else 0
    
    festivos = obtener_festivos_colombia(anio)
    
    # Contar días hábiles hasta hoy (inclusive si hoy es hábil)
    primer_dia = date(anio, mes, 1)
    dia_habil = 0
    
    dia_actual = primer_dia
    while dia_actual <= hoy:
        if es_dia_habil(dia_actual, festivos):
            dia_habil += 1
        dia_actual += timedelta(days=1)
    
    return dia_habil


def obtener_fecha_por_dia_habil(anio: int, mes: int, dia_habil: int) -> Optional[date]:
    """
    Dado un número de día hábil, retorna la fecha correspondiente en ese mes.
    
    Args:
        anio: Año
        mes: Mes (1-12)
        dia_habil: Número de día hábil (1, 2, 3, ...)
    
    Returns:
        La fecha correspondiente o None si no existe ese día hábil en el mes.
    """
    dias = obtener_dias_habiles_mes(anio, mes)
    
    for d in dias:
        if d["dia_habil"] == dia_habil:
            return date.fromisoformat(d["fecha"])
    
    return None


def comparar_dias_habiles(
    anio_actual: int, mes_actual: int,
    anio_comparar: int, mes_comparar: int,
    hasta_dia_habil: int = None
) -> Dict:
    """
    Compara los días hábiles entre dos meses.
    Permite ver el día hábil equivalente en otro mes.
    
    Args:
        anio_actual: Año del mes actual
        mes_actual: Mes actual
        anio_comparar: Año del mes a comparar
        mes_comparar: Mes a comparar
        hasta_dia_habil: Comparar hasta este día hábil (opcional)
    
    Returns:
        Dict con información de comparación
    """
    dias_mes_actual = obtener_dias_habiles_mes(anio_actual, mes_actual)
    dias_mes_comparar = obtener_dias_habiles_mes(anio_comparar, mes_comparar)
    
    # Si no se especifica, usar el día hábil actual
    if hasta_dia_habil is None:
        hasta_dia_habil = obtener_dia_habil_actual(anio_actual, mes_actual)
    
    # Buscar la fecha equivalente en cada mes
    fecha_actual = None
    fecha_comparar = None
    
    for d in dias_mes_actual:
        if d["dia_habil"] == hasta_dia_habil:
            fecha_actual = d
            break
    
    for d in dias_mes_comparar:
        if d["dia_habil"] == hasta_dia_habil:
            fecha_comparar = d
            break
    
    return {
        "dia_habil": hasta_dia_habil,
        "mes_actual": {
            "anio": anio_actual,
            "mes": mes_actual,
            "fecha": fecha_actual["fecha"] if fecha_actual else None,
            "dia_mes": fecha_actual["dia_mes"] if fecha_actual else None,
            "total_dias_habiles": len(dias_mes_actual)
        },
        "mes_comparar": {
            "anio": anio_comparar,
            "mes": mes_comparar,
            "fecha": fecha_comparar["fecha"] if fecha_comparar else None,
            "dia_mes": fecha_comparar["dia_mes"] if fecha_comparar else None,
            "total_dias_habiles": len(dias_mes_comparar)
        },
        "mapeo_completo": [
            {
                "dia_habil": i + 1,
                "fecha_actual": dias_mes_actual[i]["fecha"] if i < len(dias_mes_actual) else None,
                "fecha_comparar": dias_mes_comparar[i]["fecha"] if i < len(dias_mes_comparar) else None
            }
            for i in range(max(len(dias_mes_actual), len(dias_mes_comparar)))
        ]
    }


def obtener_total_dias_habiles_mes(anio: int, mes: int) -> int:
    """Retorna el total de días hábiles en un mes."""
    return len(obtener_dias_habiles_mes(anio, mes))


def obtener_info_dia_habil_actual() -> Dict:
    """
    Retorna información del día hábil actual.
    Útil para el frontend.
    """
    from datetime import date as dt_date
    hoy = dt_date.today()
    
    festivos = obtener_festivos_colombia(hoy.year)
    
    dia_habil_actual = obtener_dia_habil_actual(hoy.year, hoy.month)
    total_dias_mes = obtener_total_dias_habiles_mes(hoy.year, hoy.month)
    
    return {
        "fecha": hoy.isoformat(),
        "anio": hoy.year,
        "mes": hoy.month,
        "dia": hoy.day,
        "dia_habil": dia_habil_actual,
        "total_dias_habiles_mes": total_dias_mes,
        "dias_habiles_restantes": total_dias_mes - dia_habil_actual,
        "es_dia_habil": es_dia_habil(hoy, festivos),
        "festivos_mes": [f.isoformat() for f in festivos if f.month == hoy.month]
    }


# Ejemplo de uso
if __name__ == "__main__":
    # Test para diciembre 2025
    print("=== Festivos Colombia 2025 ===")
    for f in obtener_festivos_colombia(2025):
        print(f"  {f.strftime('%Y-%m-%d %A')}")
    
    print("\n=== Días hábiles Diciembre 2025 ===")
    dias_dic = obtener_dias_habiles_mes(2025, 12)
    for d in dias_dic:
        print(f"  Día {d['dia_mes']:2d} = Hábil #{d['dia_habil']}")
    
    print("\n=== Días hábiles Noviembre 2025 ===")
    dias_nov = obtener_dias_habiles_mes(2025, 11)
    for d in dias_nov:
        print(f"  Día {d['dia_mes']:2d} = Hábil #{d['dia_habil']}")
    
    print("\n=== Comparación Dic vs Nov 2025 (hasta día hábil 8) ===")
    comp = comparar_dias_habiles(2025, 12, 2025, 11, 8)
    print(f"  Dic: {comp['mes_actual']}")
    print(f"  Nov: {comp['mes_comparar']}")
