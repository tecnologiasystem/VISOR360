# Utilidad para calcular días laborables (L-V sin festivos)
from datetime import datetime, timedelta
from typing import List, Tuple

# Festivos fijos en Colombia 2024-2026
FESTIVOS_COLOMBIA = {
    2024: [
        "2024-01-01", "2024-01-08", "2024-03-25", "2024-03-28", "2024-03-29",
        "2024-05-01", "2024-05-13", "2024-06-03", "2024-06-10", "2024-07-01",
        "2024-07-20", "2024-08-07", "2024-08-19", "2024-10-14", "2024-11-04",
        "2024-11-11", "2024-12-08", "2024-12-25"
    ],
    2025: [
        "2025-01-01", "2025-01-06", "2025-03-24", "2025-04-17", "2025-04-18",
        "2025-05-01", "2025-06-02", "2025-06-23", "2025-06-30", "2025-07-20",
        "2025-08-07", "2025-08-18", "2025-10-13", "2025-11-03", "2025-11-17",
        "2025-12-08", "2025-12-25"
    ],
    2026: [
        "2026-01-01", "2026-01-12", "2026-03-23", "2026-04-02", "2026-04-03",
        "2026-05-01", "2026-05-18", "2026-06-08", "2026-06-15", "2026-06-29",
        "2026-07-20", "2026-08-07", "2026-08-17", "2026-10-12", "2026-11-02",
        "2026-11-16", "2026-12-08", "2026-12-25"
    ]
}

def es_festivo(fecha: datetime) -> bool:
    """
    Verifica si una fecha es festivo en Colombia
    """
    fecha_str = fecha.strftime("%Y-%m-%d")
    anio = fecha.year
    
    if anio in FESTIVOS_COLOMBIA:
        return fecha_str in FESTIVOS_COLOMBIA[anio]
    
    return False

def calcular_dias_laborables(mes: int, anio: int) -> Tuple[int, List[datetime]]:
    """
    Calcula los días laborables (L-V sin festivos) de un mes
    
    Returns:
        Tuple: (total_dias_laborables, lista_fechas_laborables)
    """
    # Primer y último día del mes
    primer_dia = datetime(anio, mes, 1)
    
    if mes == 12:
        ultimo_dia = datetime(anio + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = datetime(anio, mes + 1, 1) - timedelta(days=1)
    
    dias_laborables = []
    fecha_actual = primer_dia
    
    while fecha_actual <= ultimo_dia:
        # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
        if fecha_actual.weekday() < 5 and not es_festivo(fecha_actual):
            dias_laborables.append(fecha_actual)
        
        fecha_actual += timedelta(days=1)
    
    return len(dias_laborables), dias_laborables

def obtener_dia_laborable_actual(mes: int, anio: int) -> Tuple[int, int]:
    """
    Obtiene el número de día laborable actual dentro del mes
    
    Returns:
        Tuple: (numero_dia_laborable, total_dias_laborables)
        Ejemplo: (10, 22) significa "día laborable 10 de 22"
    """
    hoy = datetime.now().date()
    total_dias, dias_laborables = calcular_dias_laborables(mes, anio)
    
    # Si la fecha actual no está en el mes solicitado, retornar el último día
    if hoy.month != mes or hoy.year != anio:
        # Si es un mes futuro, no hay días transcurridos
        fecha_mes = datetime(anio, mes, 1).date()
        if hoy < fecha_mes:
            return 0, total_dias
        # Si es un mes pasado, todos los días han transcurrido
        return total_dias, total_dias
    
    # Contar cuántos días laborables han transcurrido hasta hoy
    dia_actual = 0
    for i, fecha in enumerate(dias_laborables, 1):
        if fecha.date() <= hoy:
            dia_actual = i
        else:
            break
    
    return dia_actual, total_dias

def calcular_dias_restantes(mes: int, anio: int) -> int:
    """
    Calcula cuántos días laborables quedan en el mes
    """
    dia_actual, total_dias = obtener_dia_laborable_actual(mes, anio)
    return max(0, total_dias - dia_actual)

def obtener_fechas_laborables_hasta_hoy(mes: int, anio: int) -> List[str]:
    """
    Obtiene lista de fechas laborables desde inicio del mes hasta hoy
    """
    hoy = datetime.now().date()
    _, dias_laborables = calcular_dias_laborables(mes, anio)
    
    fechas_hasta_hoy = [
        f.strftime("%Y-%m-%d") 
        for f in dias_laborables 
        if f.date() <= hoy
    ]
    
    return fechas_hasta_hoy
