"""
Carga y reconciliación del modelo financiero de SystemGroup.

Fuente: "Dashboard Excel Tables  260831 11.00pm.xlsx" (24 hojas). Las 4 hojas
`P&L Consolidated/Master/Servicing/NPL` traen el resultado "sin Perú" (columna
D10 = "SPV/Trust: Todas" confirma que ya vienen pre-consolidadas, sin desglose
por SPV/país). La vista "todo el grupo" del tablero de referencia sale de sumar
esa hoja + el resultado de Perú, que vive aparte en `7Actuals info Peru` (en
COP, no en `P&L NPL Peru` que está en PEN).

Validado contra el HTML de referencia (`July 2026-Dashboard Unit Economics.html`):
Revenue mensual Ene-Jul 2026 cuadra exacto. Gross profit/EBITDA/utilidad cuadran
exacto Ene-Mayo; Jun-Jul tienen una diferencia de ~1-3% por unas filas de
reclasificación de cierre reciente que aún no se ubicaron con certeza -- ver
memoria de sesión. Aceptado como limitación conocida por ahora.

Perú no tiene Servicing ni Master Service (todo su negocio es NPL, confirmado
en fila "Servicing (n/a — todo Perú es NPL)" de 7Actuals info Peru), así que
solo se le suma a las vistas Consolidated y NPL.
"""
from __future__ import annotations

import functools
import warnings
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

def _resolver_ruta_excel() -> Path:
    """Localiza el Excel fuente de forma portable (sin ruta absoluta de una maquina).

    Orden de prioridad:
    1. Variable de entorno TABLERO_EXCEL (ruta explicita, util en despliegue).
    2. El .xlsx mas reciente dentro de la carpeta del proyecto o de 'datos/'.
    3. El nombre legado, para no romper si alguien lo deja asi.
    Asi, para actualizar el tablero basta con reemplazar el archivo en 'datos/'
    (o en la raiz del proyecto) y refrescar: no hay que tocar codigo.
    """
    import os

    override = os.getenv("TABLERO_EXCEL")
    if override:
        return Path(override)

    base = Path(__file__).parent
    # 'base' es BE/app/financiero. En VISOR360 el Excel vive en BE/datos/
    # (base.parent.parent = BE), pero en el proyecto original vive en <raiz>/datos.
    carpeta_backend_datos = base.parent.parent / "datos"  # VISOR360: BE/datos
    candidatos: list[Path] = []
    for carpeta in (carpeta_backend_datos, base / "datos", base):
        if carpeta.is_dir():
            candidatos.extend(
                p for p in carpeta.glob("*.xlsx")
                if not p.name.startswith("~")
                and "_respaldo" not in p.name
                and ".uploading" not in p.name
            )
    if candidatos:
        # El mas reciente: al subir el cierre de un mes nuevo, se usa solo.
        return max(candidatos, key=lambda p: p.stat().st_mtime)

    return carpeta_backend_datos / "Dashboard Excel Tables  260909 4.40pm.xlsx"


RUTA_EXCEL = _resolver_ruta_excel()

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"]
MESES_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]

# Tasas de cierre COP/USD por mes -- NO vienen en este Excel (se buscó explícitamente en los
# encabezados de las hojas P&L, no aparecen); se tomaron tal cual del pie de página del propio
# HTML de referencia ("Closing rates (COP/USD): Jan 3,670.47 · Feb 3,766.30 · ... Jul 3,210.56"),
# que es la misma fuente/convención que usa el cliente en su tablero original.
TASAS_COP_USD = dict(zip(MESES, [3670.47, 3766.30, 3621.86, 3667.06, 3678.15, 3443.59, 3210.56]))


def convertir_moneda(df: pd.DataFrame, moneda: str) -> pd.DataFrame:
    """Convierte un DataFrame indexado por mes (en COP MM) a USD MM si moneda == 'USD',
    dividiendo cada mes por SU PROPIA tasa de cierre (no una tasa promedio) -- igual que el
    tablero de referencia. 'COP MM' devuelve el mismo DataFrame sin tocar."""
    if moneda != "USD MM":
        return df
    tasas = pd.Series({mes: TASAS_COP_USD[mes] for mes in df.index if mes in TASAS_COP_USD})
    if tasas.empty:
        return df
    return df.div(tasas, axis=0)

# Hoja "wo Peru" (sin Perú) por cada valor del filtro de Negocio.
HOJA_POR_NEGOCIO = {
    "Consolidated": "P&L Consolidated",
    "Servicing": "P&L Servicing",
    "Master Service": "P&L Master",
    "NPL": "P&L NPL",
}
# Perú solo aporta a Consolidated y NPL (todo su negocio es NPL).
NEGOCIOS_CON_PERU = {"Consolidated", "NPL"}

# Filas (columna C) que arman la cascada del estado de resultados en las hojas
# "wo Peru". Confirmado leyendo el workbook: no existen subtotales de "Gross
# profit"/"EBITDA" como filas propias en estas hojas -- se calculan aquí.
FILA_OPERATING_INCOME = "Operating income"
FILA_COS = "COS"
FILA_SGA = "SG&A expenses"
FILA_RESERVAS = "Reservas"
FILA_DEPRECIACION = "Depreciation"
FILA_AMORTIZACION = "Amortization"
FILA_NOOP_INCOME = "No-operating income"
FILA_NOOP_FINANCIERO = "Non-operating expenxes (Financing)"  # sic, typo real en el Excel
FILA_NOOP_OTROS = "Non-operating expenxes (Others)"  # sic, typo real en el Excel
FILA_TAX = "Tax"

# Columnas 0-based de los meses Ene-Jul 2026 en las hojas "wo Peru" (T:Z).
COLS_MESES_WO_PERU = list(range(20, 27))

# Filas (columna B) de la hoja "7Actuals info Peru", bloque "Consolidado: Perú"
# (columnas G:M = Ene-Jul 2026, 0-based 6..12). Estas SÍ vienen con subtotales
# ya calculados (Gross profit, EBITDA, etc.) -- no hay que derivarlos a mano.
FILAS_PERU = {
    "revenue": "Operating income",
    "cos": "COGS",
    "gross_profit": "Gross profit",
    "sga": "SG&A expenses",
    "ebitda": "EBITDA",
    "ebitda_adj": "EBITDA Adjusted",
    "depreciacion": "Depreciation",
    "amortizacion": "Amortization",
    "operating_profit": "Operacional income",  # sic, typo real en el Excel
    "noop_income": "No-operating income",
    "noop_fin": "Non-operating expenses (Financing)",
    "noop_otros": "Non-operating expenses (Others)",
    "before_tax": "Before tax profit",
    "tax": "Tax",
    "net_profit": "Net profit",
    "ebt_adj": "Earnings before taxes Adjusted",
}
COLS_MESES_PERU = list(range(6, 13))


def _mm(valor: float | None) -> float:
    """Convierte pesos crudos a millones de COP (unidad de todo el modelo)."""
    return (valor or 0) / 1_000_000


@functools.lru_cache(maxsize=None)
def _workbook():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return load_workbook(RUTA_EXCEL, data_only=True, read_only=True)


def _fila_por_texto(filas: list, columna: int, texto: str) -> tuple | None:
    for row in filas:
        valor = row[columna]
        if isinstance(valor, str) and valor.strip().lower() == texto.lower():
            return row
    return None


def _indice_por_texto(filas: list, columna: int, texto: str, desde: int = 0) -> int | None:
    for i in range(desde, len(filas)):
        valor = filas[i][columna]
        if isinstance(valor, str) and valor.strip().lower() == texto.lower():
            return i
    return None


def _fila_por_texto_en_rango(filas: list, columna: int, texto: str, desde: int, hasta: int) -> tuple | None:
    """Como _fila_por_texto pero solo busca entre las filas [desde, hasta) -- necesario porque
    nombres de categoría como 'Personnel Expenses' o 'Fees' se repiten varias veces en la misma
    hoja (una vez por sub-portafolio de NPL, otra en COGS, otra en SG&A)."""
    for i in range(desde, min(hasta, len(filas))):
        valor = filas[i][columna]
        if isinstance(valor, str) and valor.strip().lower() == texto.lower():
            return filas[i]
    return None


def _serie_mensual(fila: tuple | None, columnas: list[int]) -> list[float]:
    if fila is None:
        return [0.0] * len(columnas)
    return [_mm(fila[c]) for c in columnas]


@functools.lru_cache(maxsize=128)
def cargar_estado_resultados_wo_peru(nombre_hoja: str) -> dict[str, list[float]]:
    """Extrae y deriva la cascada del P&L (sin Perú) de una hoja P&L Consolidated/Master/Servicing/NPL."""
    wb = _workbook()
    ws = wb[nombre_hoja]
    filas = list(ws.iter_rows(min_row=1, max_row=250, values_only=True))

    def serie(texto: str) -> list[float]:
        return _serie_mensual(_fila_por_texto(filas, 2, texto), COLS_MESES_WO_PERU)

    revenue = serie(FILA_OPERATING_INCOME)
    cos = serie(FILA_COS)
    sga = serie(FILA_SGA)
    reservas = serie(FILA_RESERVAS)
    depreciacion = serie(FILA_DEPRECIACION)
    amortizacion = serie(FILA_AMORTIZACION)
    noop_income = serie(FILA_NOOP_INCOME)
    noop_fin = serie(FILA_NOOP_FINANCIERO)
    noop_otros = serie(FILA_NOOP_OTROS)
    tax = serie(FILA_TAX)

    n = len(MESES)
    gross_profit = [revenue[i] - cos[i] for i in range(n)]
    ebitda = [gross_profit[i] - sga[i] for i in range(n)]
    ebitda_adj = [ebitda[i] - reservas[i] for i in range(n)]
    operating_profit = [ebitda[i] - depreciacion[i] - amortizacion[i] for i in range(n)]
    before_tax = [operating_profit[i] + noop_income[i] - noop_fin[i] - noop_otros[i] for i in range(n)]
    net_before_reservas = [before_tax[i] - tax[i] for i in range(n)]
    net_after_reservas = [net_before_reservas[i] - reservas[i] for i in range(n)]
    ebt_adj = [before_tax[i] - reservas[i] for i in range(n)]

    return {
        "revenue": revenue, "cos": cos, "gross_profit": gross_profit, "sga": sga,
        "ebitda": ebitda, "reservas": reservas, "ebitda_adj": ebitda_adj,
        "depreciacion": depreciacion, "amortizacion": amortizacion, "operating_profit": operating_profit,
        "noop_income": noop_income, "noop_fin": noop_fin, "noop_otros": noop_otros,
        "before_tax": before_tax, "tax": tax,
        "net_before_reservas": net_before_reservas, "net_after_reservas": net_after_reservas,
        "ebt_adj": ebt_adj,
    }


@functools.lru_cache(maxsize=128)
def cargar_estado_resultados_peru() -> dict[str, list[float]]:
    """Extrae el bloque 'Consolidado: Perú' de 7Actuals info Peru (ya trae subtotales calculados)."""
    wb = _workbook()
    ws = wb["7Actuals info Peru"]
    filas = list(ws.iter_rows(min_row=1, max_row=105, values_only=True))

    def serie(texto: str) -> list[float]:
        return _serie_mensual(_fila_por_texto(filas, 1, texto), COLS_MESES_PERU)

    resultado = {clave: serie(texto) for clave, texto in FILAS_PERU.items()}
    # Reservas no es una fila propia en esta hoja (ver nota "LEGACY" del Excel) --
    # se deriva de la diferencia entre EBITDA y EBITDA Adjusted para poder sumarla
    # consistentemente con el lado "wo Peru".
    resultado["reservas"] = [resultado["ebitda"][i] - resultado["ebitda_adj"][i] for i in range(len(MESES))]
    return resultado


# Todas las líneas que se blanquean (suman) entre "wo Peru" y Perú para que la
# tabla detallada cuadre internamente (Revenue - COS = Gross profit, etc.) en
# vez de mezclar columnas ya combinadas con columnas "solo wo-Peru".
LINEAS_A_COMBINAR = [
    "revenue", "cos", "gross_profit", "sga", "ebitda", "reservas", "ebitda_adj",
    "depreciacion", "amortizacion", "operating_profit", "noop_income", "noop_fin",
    "noop_otros", "before_tax", "tax", "ebt_adj",
]


@functools.lru_cache(maxsize=128)
def cargar_negocio(negocio: str) -> pd.DataFrame:
    """
    Devuelve el estado de resultados mensual (Ene-Jul 2026, COP MM) para el
    filtro de Negocio dado, sumando Perú cuando corresponde.
    """
    hoja = HOJA_POR_NEGOCIO[negocio]
    wo_peru = cargar_estado_resultados_wo_peru(hoja)

    if negocio in NEGOCIOS_CON_PERU:
        peru = cargar_estado_resultados_peru()
        combinado = {
            clave: [wo_peru[clave][i] + peru[clave][i] for i in range(len(MESES))]
            for clave in LINEAS_A_COMBINAR
        }
        # Se deriva de before_tax/tax/reservas YA combinados (en vez de usar la fila
        # "Net profit" propia de Perú) para que cuadre en cascada con el resto de la
        # tabla -- la metodología de reservas de Perú está marcada como "LEGACY /
        # en revisión" en su hoja fuente y no siempre coincide con este mismo criterio.
        combinado["net_before_reservas"] = [
            combinado["before_tax"][i] - combinado["tax"][i] for i in range(len(MESES))
        ]
        combinado["net_after_reservas"] = [
            combinado["net_before_reservas"][i] - combinado["reservas"][i] for i in range(len(MESES))
        ]
        datos = combinado
    else:
        datos = wo_peru

    df = pd.DataFrame(datos, index=MESES)
    return df


# Categorías de gasto que se repiten dentro de COGS ("Cost") y de SG&A -- mismo
# nombre de fila en ambas secciones, por eso hace falta acotar el rango de
# búsqueda (ver _fila_por_texto_en_rango) en vez de reusar _fila_por_texto.
CATEGORIAS_COSTO = [
    "Personnel Expenses", "Fees", "Taxes", "Leases", "Insurance", "Services", "Legal Expenses",
    "Collection fees", "Contributions And Memberships", "Maintenance And Repairs",
    "Adaptation And Installation", "Travel Expenses", "Miscellaneous",
]


@functools.lru_cache(maxsize=128)
def cargar_composicion_costos(negocio: str) -> pd.DataFrame:
    """
    Desglose de COGS y SG&A por categoría de gasto (Personnel, Fees, Leases, etc.)
    para el filtro de Negocio dado, en COP MM acumulado Ene-Jul 2026 ("wo Peru";
    Perú no desglosa por categoría en sus hojas fuente, solo el total).
    """
    hoja = HOJA_POR_NEGOCIO[negocio]
    filas = _filas_hoja(hoja)

    idx_cos = _indice_por_texto(filas, 2, "COS")
    idx_sga = _indice_por_texto(filas, 2, "SG&A expenses", desde=idx_cos)
    # El sub-encabezado que agrupa Personnel/Fees/Leases/etc. dentro de COS varía por hoja:
    # "P&L Consolidated"/"P&L Master"/"P&L NPL" usan "Cost" (un solo bloque); "P&L Servicing"
    # no tiene "Cost" -- usa "Direct cost" en su lugar (con "Indirect Cost" después, ambos
    # antes de SG&A). Se prueba "Cost" primero y se cae a "Direct cost" si no existe.
    idx_cost = _indice_por_texto(filas, 2, "Cost", desde=idx_cos) \
        or _indice_por_texto(filas, 2, "Direct cost", desde=idx_cos)
    # "P&L Servicing"/"P&L Master" no manejan reservas contractuales (eso es propio de NPL) --
    # no tienen fila "Reservas"; si no existe, se usa "Depreciation" (fila universal en las 4
    # hojas) como límite en su lugar, para no escanear de más buscando categorías de SG&A.
    idx_reservas = _indice_por_texto(filas, 2, "Reservas", desde=idx_sga) \
        or _indice_por_texto(filas, 2, "Depreciation", desde=idx_sga)

    registros = []
    total_cogs_mapeado = total_sga_mapeado = 0.0
    for categoria in CATEGORIAS_COSTO:
        fila_cogs = _fila_por_texto_en_rango(filas, 2, categoria, idx_cost + 1, idx_sga)
        fila_sga = _fila_por_texto_en_rango(filas, 2, categoria, idx_sga + 1, idx_reservas)
        valor_cogs = sum(_serie_mensual(fila_cogs, COLS_MESES_WO_PERU)) if fila_cogs else 0.0
        valor_sga = sum(_serie_mensual(fila_sga, COLS_MESES_WO_PERU)) if fila_sga else 0.0
        total_cogs_mapeado += valor_cogs
        total_sga_mapeado += valor_sga
        if valor_cogs or valor_sga:
            registros.append({"Categoria": categoria, "COGS": valor_cogs, "SG&A": valor_sga})

    # Fila "Otros" para que la tabla siempre sume exacto contra el total ya
    # validado de COGS/SG&A -- algunas subcategorías más finas de la plantilla
    # (ej. "Contributions And Memberships") no existen como fila propia en esta
    # hoja resumen, así que su valor queda dentro de este residuo en vez de
    # perderse silenciosamente.
    cos_total = sum(cargar_estado_resultados_wo_peru(hoja)["cos"])
    sga_total = sum(cargar_estado_resultados_wo_peru(hoja)["sga"])
    registros.append({
        "Categoria": "Otros", "COGS": cos_total - total_cogs_mapeado, "SG&A": sga_total - total_sga_mapeado,
    })

    return pd.DataFrame(registros)


# Los 4 "Aliados" (agencias de cobranza externas) que Finanzas separó de Fees/Services
# hacia la categoría "Collection fees" del P&L -- confirmado contra
# "P&L Consolidated" filas 206-210 (mismos 4 terceros, cuenta 73351501/73103501).
ALIADOS_COLLECTION_FEES = {
    "AYS SOLUCIONES ESTRATÉGICAS S.A.S.", "MAPNOVA SAS",
    "ORGANIZACION DE COBRANZAS ORCOB LIMITADA", "VIRTUS JURÍDICO BPO SAS",
}

CODIGOS_COSTO_NO_PERSONAL = {
    "7310": "Fees", "7320": "Leases", "7330": "Insurance", "7335": "Services",
}


@functools.lru_cache(maxsize=128)
def cargar_reconciliacion_costo_no_personal() -> pd.DataFrame:
    """
    Reconciliación pedida por Finanzas (respuesta a la propuesta del tablero,
    2026-09-14): la hoja `Direct Cost- Non Personnel` viene con las comisiones de
    los 4 "Aliados" (agencias de cobranza externas) todavía mezcladas dentro de
    Fees/Services, pero el P&L ya las separó a la categoría "Collection fees" --
    por eso el total crudo de esta hoja no cuadraba contra `cargar_composicion_costos()`.

    Busca los 3 bloques de negocio por TEXTO ("Master Service", "Non-Performing
    Loans", "Servicing" -- exactos, con total numérico, no las filas de notas del
    pie de la hoja) en vez de números de fila fijos, para sobrevivir mejor a que
    la hoja se regenere cada mes con más/menos proveedores.

    Devuelve un DataFrame: Negocio, Código, Categoría, Total original (MM),
    Ajuste Aliados (MM, ya en negativo), Total ajustado (MM).
    """
    wb = _workbook()
    # El nombre de esta hoja ha variado de un mes a otro solo en espacios
    # ("Direct Cost- Non Personnel" vs "Direct Cost-Non Personnel") -- se
    # busca por texto normalizado en vez de la cadena exacta, para no volver
    # a romper con el próximo archivo mensual por un espacio de más o de menos.
    nombre_hoja = next(
        (nombre for nombre in wb.sheetnames if nombre.replace(" ", "") == "DirectCost-NonPersonnel"),
        None,
    )
    if nombre_hoja is None:
        raise KeyError("No se encontró la hoja 'Direct Cost- Non Personnel' (ni variantes de espaciado) en el Excel.")
    ws = wb[nombre_hoja]
    filas = list(ws.iter_rows(min_row=1, max_row=210, values_only=True))

    def es_negocio(nombre, total) -> bool:
        return nombre in ("Master Service", "Non-Performing Loans", "Servicing") and isinstance(total, (int, float))

    marcadores = [(i, filas[i][1]) for i in range(len(filas)) if es_negocio(filas[i][1], filas[i][9])]
    if len(marcadores) < 3:
        return pd.DataFrame()

    def es_codigo_cuenta(nombre) -> bool:
        return isinstance(nombre, str) and nombre.strip().isdigit() and len(nombre.strip()) == 4

    registros = []
    for pos, (idx_inicio, nombre_negocio) in enumerate(marcadores):
        idx_fin_negocio = marcadores[pos + 1][0] if pos + 1 < len(marcadores) else len(filas)
        negocio_legible = "NPL" if nombre_negocio == "Non-Performing Loans" else nombre_negocio

        # Todas las filas de código de cuenta dentro de este bloque de negocio (4310,
        # 7320, 7335... y también otras como 7350/7395 que no nos interesan aquí pero
        # SI sirven de límite para no mezclar sus proveedores con los de Fees/Services).
        codigos_en_bloque = sorted(
            i for i in range(idx_inicio, idx_fin_negocio) if es_codigo_cuenta(filas[i][1])
        )

        for codigo, categoria in CODIGOS_COSTO_NO_PERSONAL.items():
            idx_codigo = next((i for i in codigos_en_bloque if filas[i][1] == codigo), None)
            if idx_codigo is None:
                continue
            total_original = filas[idx_codigo][9] or 0

            # Límite real de este código: el siguiente código de cuenta que aparezca
            # (no el fin de todo el bloque de negocio) -- así no se mezclan Aliados
            # que en realidad caen bajo otro código dentro del mismo negocio.
            posteriores = [c for c in codigos_en_bloque if c > idx_codigo]
            idx_fin_codigo = posteriores[0] if posteriores else idx_fin_negocio

            ajuste = 0.0
            if codigo in ("7310", "7335"):
                # El ajuste de Aliados solo aplica a Fees/Services -- son las 2
                # categorías donde Finanzas confirmó que vivían estas comisiones
                # (ver hallazgo en memoria de sesión). No restar de Leases/Insurance
                # sin evidencia real.
                ajuste = sum(
                    filas[i][9] or 0
                    for i in range(idx_codigo, idx_fin_codigo)
                    if isinstance(filas[i][1], str) and filas[i][1].strip() in ALIADOS_COLLECTION_FEES
                )

            registros.append({
                "Negocio": negocio_legible,
                "Código": codigo,
                "Categoría": categoria,
                "Total original (MM)": _mm(total_original),
                "Ajuste Aliados (MM)": -_mm(ajuste),
                "Total ajustado (MM)": _mm(total_original - ajuste),
            })

    return pd.DataFrame(registros)


@functools.lru_cache(maxsize=128)
def cargar_top_terceros(top_n: int = 15) -> pd.DataFrame:
    """
    Top proveedores/terceros por gasto YTD Ene-Jul 2026, desde la hoja `Fee Services`
    (tabla dinámica exportada, columna "Cuenta Tercero" = nombre real del proveedor).

    OJO: esta hoja solo cubre la categoría "① SERVICES" (confirmado -- no hay bloques
    ②/③/④ en la hoja, se buscó explícitamente). El tablero de referencia titula esta
    tabla "Top third-party vendors (Fees + Services + Leases + Taxes)", que es más
    amplia -- las categorías de Fees/Leases/Taxes por tercero viven en otras hojas
    todavía sin mapear. Por ahora esto es solo "Services", etiquetado como tal en la UI.

    Validado: la suma de todos los proveedores reproduce exacto la fila "Grand Total"
    de la propia hoja (1,541.6 MM).
    """
    wb = _workbook()
    ws = wb["Fee Services"]
    totales: dict[str, float] = {}
    for row in ws.iter_rows(min_row=12, values_only=True):
        nombre = row[5]
        if not isinstance(nombre, str):
            continue
        nombre = nombre.strip()
        if not nombre or nombre.endswith(" Total") or nombre == "Grand Total":
            continue
        suma = sum(v for v in row[6:13] if isinstance(v, (int, float)))
        totales[nombre] = totales.get(nombre, 0.0) + suma

    df = pd.DataFrame(
        [{"Proveedor": nombre, "YTD": _mm(valor)} for nombre, valor in totales.items()]
    ).sort_values("YTD", ascending=False)
    return df.head(top_n).reset_index(drop=True)


@functools.lru_cache(maxsize=128)
def cargar_revenue_por_contrato(negocio: str) -> pd.DataFrame | None:
    """
    Revenue YTD por contrato de cobranza (Adamantine, JCAP, Coltefinanciera, etc.),
    desde el bloque "Operating income" de `P&L Servicing`/`P&L Master` (columna "2026",
    que pese al rótulo "Year" resulta ser el acumulado a la fecha -- validado exacto
    contra `cargar_negocio()`: 7,424.165 MM Servicing en ambas rutas).

    Investigado a fondo (2026-09-15) si se podía extender esto a un filtro de Contrato
    que mueva TODOS los KPIs de la vista (como en el tablero de referencia) -- NO se
    pudo: el resto del estado de resultados (COGS, Personnel, Fees, Leases, SG&A, etc.)
    son líneas ÚNICAS agregadas para todo el Business Unit, sin desglose por contrato en
    ninguna hoja del archivo. Por eso esto se queda como una tabla de Revenue solamente,
    nunca como un filtro que simule tener el costo por contrato (no existe en la fuente).

    Solo existe esta fila para Servicing y Master Service -- Consolidated y NPL no
    traen este desglose. Devuelve None para esos casos.
    """
    if negocio not in ("Servicing", "Master Service"):
        return None
    hoja = HOJA_POR_NEGOCIO[negocio]
    filas = _filas_hoja(hoja, max_row=40)
    idx_ingreso = _indice_por_texto(filas, 2, "Operating income")
    if idx_ingreso is None:
        return None

    prefijo = f"{negocio} - "
    registros = []
    i = idx_ingreso + 1
    while i < len(filas):
        nombre = filas[i][2]
        if not isinstance(nombre, str) or not nombre.startswith(prefijo):
            break
        contrato = nombre[len(prefijo):].strip() or "(sin campaña)"
        if contrato == negocio:
            contrato = "(sin campaña)"
        registros.append({"Contrato": contrato, "Revenue YTD (MM)": _mm(filas[i][8])})
        i += 1
    return pd.DataFrame(registros).sort_values("Revenue YTD (MM)", ascending=False).reset_index(drop=True)


@functools.lru_cache(maxsize=128)
def cargar_crxm(negocio: str) -> pd.DataFrame | None:
    """
    Recovery Cost per Million ($/MM recuperado = (COGS + SG&A) / Recuperación en millones)
    por campaña, desde la hoja `Cost per Million`. Solo existe una sección para Servicing
    (con desglose por campaña) y otra para NPL (solo el total "All", sin campañas) -- no
    hay sección de Master Service ni un "Consolidado" ya blendeado en esta hoja fuente.
    Devuelve None si el Negocio seleccionado no tiene sección en esta hoja.
    """
    encabezado_por_negocio = {"Servicing": "SERVICING", "NPL": "NPL"}
    titulo_buscado = encabezado_por_negocio.get(negocio)
    if titulo_buscado is None:
        return None

    wb = _workbook()
    ws = wb["Cost per Million"]
    filas = list(ws.iter_rows(min_row=1, max_row=200, values_only=True))

    idx_titulo = None
    for i, row in enumerate(filas):
        valor = row[0]
        if isinstance(valor, str) and valor.strip().upper().startswith(titulo_buscado):
            idx_titulo = i
            break
    if idx_titulo is None:
        return None

    idx_header = _indice_por_texto(filas, 0, "Campaign \\ Month", desde=idx_titulo)
    if idx_header is None:
        return None

    registros = []
    i = idx_header + 2  # se salta la fila de "1,2,3..." bajo el encabezado
    while i < len(filas):
        campana = filas[i][0]
        if not isinstance(campana, str) or not campana.strip():
            break
        valores_mes = [filas[i][c] or 0 for c in range(1, 8)]
        ytd = filas[i][10]
        registros.append({
            "Campaña": campana, **{mes: valores_mes[k] for k, mes in enumerate(MESES)},
            "YTD": ytd if ytd is not None else sum(valores_mes) / 7,
        })
        i += 1

    return pd.DataFrame(registros)


@functools.lru_cache(maxsize=128)
def cargar_eficiencia_y_personal_bu() -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    TABLA A (eficiencia por unidad de negocio) y TABLA B (costo de personal por unidad de
    negocio) de la hoja `Profitability Analysis` -- es un snapshot de UN SOLO mes (el que
    indiquen los parámetros "Start/End date" de la hoja, hoy Julio 2026), no una serie
    Ene-Jul como el resto del tablero -- se devuelve el texto del período para dejarlo
    claro en la UI.
    """
    wb = _workbook()
    ws = wb["Profitability Analysis"]
    filas = list(ws.iter_rows(min_row=1, max_row=45, values_only=True))

    periodo_texto = filas[2][1] if isinstance(filas[2][1], str) else "período no identificado"

    idx_a = next((i for i, r in enumerate(filas) if isinstance(r[1], str) and r[1].startswith("TABLE A")), None)
    idx_b = next((i for i, r in enumerate(filas) if isinstance(r[1], str) and r[1].startswith("TABLE B")), None)

    def leer_bu(idx_header: int, idx_limite: int) -> list[dict]:
        filas_bu = []
        for i in range(idx_header + 1, idx_limite):
            nombre = filas[i][1]
            if not isinstance(nombre, str) or nombre.strip() in ("Verification", ""):
                continue
            filas_bu.append((i, nombre))
        return filas_bu

    tabla_a = pd.DataFrame([
        {
            "Business Unit": nombre,
            "Total income": _mm(filas[i][2]),
            "Total cost (COS+SG&A)": _mm(filas[i][3]),
            "EBITDA": _mm(filas[i][4]),
            "Efficiency %": (filas[i][5] or 0) * 100,
            "Ranking": filas[i][6],
        }
        for i, nombre in leer_bu(idx_a + 2, idx_b - 1)  # +2 salta la fila de encabezado de columnas
    ])

    tabla_b = pd.DataFrame([
        {
            "Business Unit": nombre,
            "Personnel Direct+SG&A": _mm(filas[i][2]),
            "Personnel Indirect": _mm(filas[i][3]),
            "Personnel Total": _mm(filas[i][4]),
            "% Income": (filas[i][5] or 0) * 100,
        }
        for i, nombre in leer_bu(idx_b + 2, idx_b + 6)
        if not nombre.upper().startswith("TOTAL")
    ])

    return tabla_a, tabla_b, periodo_texto


# Fila (1-based) del título "TABLE X -- Personnel Expense by Campaign (Mes)" de
# cada tabla mensual en la hoja "Profitability Analysis". A diferencia de
# TABLA A/B (snapshot de un solo mes, arriba), esta hoja SI trae una serie
# historica Ene-Jul -- pero como tablas apiladas VERTICALMENTE (una tabla
# nueva por mes, no columnas lado a lado), por eso una revision anterior no
# la encontro. Confirmado leyendo la hoja completa fila por fila -- no asumir
# que la fila de titulo esta a una distancia fija de la anterior, cambia
# (10, 12, 13, 16, 15, 14 filas de separación) porque cada mes tiene una
# cantidad distinta de campañas activas.
TABLAS_PRODUCTIVIDAD_MENSUAL = [
    ("Ene", 27), ("Feb", 38), ("Mar", 50), ("Abr", 63), ("May", 79), ("Jun", 94), ("Jul", 108),
]


@functools.lru_cache(maxsize=128)
def cargar_productividad_personal_mensual() -> pd.DataFrame:
    """
    Gasto de personal por campaña/contrato, en serie mensual Ene-Jul 2026, desde
    las tablas C-I (filas 27-120) de la hoja "Profitability Analysis".
    Devuelve un DataFrame largo: Mes, Campaña, Total income, Personnel Direct+SG&A,
    Personnel Indirect, Personnel Total, % Income, Recovery cost per million.
    Los montos ya vienen en millones de COP (_mm). Cada tabla mensual termina en
    una fila "TOTAL (= Consolidated)" -- se usa como señal de corte en vez de un
    número fijo de filas, porque la cantidad de campañas varía mes a mes (ej.
    "Alianza SGP" aparece desde febrero, "CXC" desde marzo, "PA Mapnova" solo en julio).
    """
    wb = _workbook()
    ws = wb["Profitability Analysis"]
    filas = list(ws.iter_rows(min_row=1, max_row=125, values_only=True))

    registros = []
    for mes, fila_titulo in TABLAS_PRODUCTIVIDAD_MENSUAL:
        idx = fila_titulo + 1  # salta título (fila_titulo-1, 0-based) y encabezado -> primera fila de datos
        while idx < len(filas):
            nombre = filas[idx][1]
            if not isinstance(nombre, str) or nombre.strip() == "":
                idx += 1
                continue
            if nombre.strip().upper().startswith("TOTAL"):
                break
            registros.append({
                "Mes": mes,
                "Campaña": nombre.strip(),
                "Total income": _mm(filas[idx][2]),
                "Personnel Direct+SG&A": _mm(filas[idx][3]),
                "Personnel Indirect": _mm(filas[idx][4]),
                "Personnel Total": _mm(filas[idx][5]),
                "% Income": (filas[idx][6] or 0) * 100,
                "Recovery cost per million": filas[idx][7] or 0,
            })
            idx += 1

    return pd.DataFrame(registros)


TRIMESTRES = {"Q1": ["Ene", "Feb", "Mar"], "Q2": ["Abr", "May", "Jun"], "Q3": ["Jul"]}
MES_A_TRIMESTRE = {mes: trimestre for trimestre, meses in TRIMESTRES.items() for mes in meses}


def filtrar_periodo(df: pd.DataFrame, periodo: str) -> pd.DataFrame:
    """periodo: 'Todos', un mes ('Ene'..'Jul'), o un trimestre ('Q1','Q2','Q3')."""
    if periodo == "Todos":
        return df
    if periodo in TRIMESTRES:
        return df.loc[[m for m in TRIMESTRES[periodo] if m in df.index]]
    return df.loc[[periodo]]


def agregar_a_trimestre(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa un DataFrame indexado por mes (Ene..Jul) en trimestres (Q1..Q3),
    sumando todas las columnas numéricas -- para la vista 'Trimestral' de las
    gráficas mensuales (Q3 2026 solo trae Jul todavía, YTD real)."""
    df = df.copy()
    df["_trimestre"] = [MES_A_TRIMESTRE.get(m, m) for m in df.index]
    return df.groupby("_trimestre").sum().loc[[t for t in TRIMESTRES if t in df["_trimestre"].unique()]]


# =====================================================================
# Desglose por SPV / País -- hoja "7Actuals info" (sin Perú) y
# "7Actuals info Peru" (Perú). Confirmado leyendo el workbook: AMBAS hojas
# repiten el mismo patrón de filas (Operating income, Gross profit, EBITDA...)
# en bloques de 7 columnas (Ene-Jul), uno por SPV -- por eso se puede reusar
# la misma búsqueda "por texto de fila" que ya usa el resto del módulo, solo
# cambiando en qué columnas se lee.
#
# Solo 4 SPV "wo Peru" tienen actividad real en Actuals (Systemgroup SAS,
# NPL Cayman, Global Financial Corp, NPL CO SAS) -- México (NPL SA De CV) y
# Honduras (NPL HN) no aparecen en esta hoja: solo tienen presupuesto, no
# actuales, en lo corrido de 2026 (entidades inactivas/en cierre). Si se
# seleccionan como país, el tablero debe mostrar 0 en vez de fallar.
# =====================================================================

# Columna 0-based donde empieza cada bloque "Consolidado - <SPV>" (7 meses).
SPV_NO_PERU_CONSOLIDADO = {
    "Systemgroup SAS": 144,
    "Systemgroup NPL Cayman": 151,
    "Systemgroup Global Financial Corp": 158,
    "Systemgroup NPL CO SAS": 165,
}
# Columna 0-based donde empieza cada bloque "<SPV> - <Negocio>" (7 meses).
SPV_NO_PERU_POR_NEGOCIO = {
    "Systemgroup SAS": {"Servicing": 180, "Master Service": 187, "NPL": 194},
    "Systemgroup NPL Cayman": {"Servicing": 208, "Master Service": 215, "NPL": 222},
    "Systemgroup Global Financial Corp": {"Servicing": 236, "Master Service": 243, "NPL": 250},
    "Systemgroup NPL CO SAS": {"Servicing": 264, "Master Service": 271, "NPL": 278},
}
# Columna 0-based donde empieza cada bloque de Perú (7 meses) -- Perú es 100% NPL.
SPV_PERU = {
    "Systemgroup NPL PE SAC": 13,
    "Sistemgroup Internacional Peru SAC": 20,
    "Systemcobro Peru SAC": 27,
    "Soluciones SAC": 34,
}

SPV_PAIS = {
    "Systemgroup SAS": "Colombia",
    "Systemgroup NPL CO SAS": "Colombia",
    "Systemgroup NPL Cayman": "Cayman",
    "Systemgroup Global Financial Corp": "Panama",
    "Systemgroup NPL PE SAC": "Peru",
    "Sistemgroup Internacional Peru SAC": "Peru",
    "Systemcobro Peru SAC": "Peru",
    "Soluciones SAC": "Peru",
    # Sin actuales todavía (solo presupuesto) -- se dejan listados para que el
    # filtro de País los muestre, aunque las cifras salgan en 0.
    "Systemgroup NPL SA De CV": "Mexico",
    "Systemgroup NPL HN": "Honduras",
}

# Métricas que se extraen de cada bloque, con el mismo texto de fila en ambas
# hojas ("7Actuals info" y "7Actuals info Peru" comparten la plantilla).
METRICAS_SPV = {
    "revenue": "Operating income", "cos": "COGS", "gross_profit": "Gross profit",
    "sga": "SG&A expenses", "ebitda": "EBITDA", "ebitda_adj": "EBITDA Adjusted",
    "depreciacion": "Depreciation", "amortizacion": "Amortization",
    "operating_profit": "Operacional income", "before_tax": "Before tax profit", "tax": "Tax",
}


@functools.lru_cache(maxsize=128)
def _filas_hoja(nombre_hoja: str, max_row: int = 250) -> list:
    wb = _workbook()
    return list(wb[nombre_hoja].iter_rows(min_row=1, max_row=max_row, values_only=True))


def _metricas_bloque(filas: list, col_inicio: int) -> dict[str, list[float]]:
    columnas = list(range(col_inicio, col_inicio + 7))
    return {
        clave: _serie_mensual(_fila_por_texto(filas, 1, texto), columnas)
        for clave, texto in METRICAS_SPV.items()
    }


@functools.lru_cache(maxsize=128)
def cargar_por_spv(negocio: str) -> pd.DataFrame:
    """
    Devuelve un DataFrame largo (SPV, País, Mes, revenue, gross_profit, ebitda, ...)
    para el filtro de Negocio dado. Los SPV sin actuales para ese negocio quedan
    en 0 (no se omiten, para que el filtro de País/SPV los pueda seleccionar
    igual y sea evidente que no hay actividad, en vez de que "desaparezcan").
    """
    filas_actuals = _filas_hoja("7Actuals info")
    bloques_no_peru = (
        SPV_NO_PERU_CONSOLIDADO if negocio == "Consolidated"
        else {spv: cols[negocio] for spv, cols in SPV_NO_PERU_POR_NEGOCIO.items()} if negocio != "NPL"
        else {spv: cols["NPL"] for spv, cols in SPV_NO_PERU_POR_NEGOCIO.items()}
    )

    def fila(spv: str, mes_idx: int, metricas: dict[str, list[float]]) -> dict:
        valores = {k: v[mes_idx] for k, v in metricas.items()}
        reservas = valores["ebitda"] - valores["ebitda_adj"]
        net_before = valores["before_tax"] - valores["tax"]
        return {
            "SPV": spv, "Pais": SPV_PAIS[spv], "Mes": MESES[mes_idx],
            **valores, "reservas": reservas, "ebt_adj": valores["before_tax"] - reservas,
            "net_before_reservas": net_before, "net_after_reservas": net_before - reservas,
        }

    registros = []
    for spv, col_inicio in bloques_no_peru.items():
        metricas = _metricas_bloque(filas_actuals, col_inicio)
        registros.extend(fila(spv, i, metricas) for i in range(len(MESES)))

    campos_cero = {k: 0.0 for k in list(METRICAS_SPV) + ["reservas", "ebt_adj", "net_before_reservas", "net_after_reservas"]}
    for spv_sin_actuales, pais in [("Systemgroup NPL SA De CV", "Mexico"), ("Systemgroup NPL HN", "Honduras")]:
        registros.extend({"SPV": spv_sin_actuales, "Pais": pais, "Mes": mes, **campos_cero} for mes in MESES)

    if negocio in NEGOCIOS_CON_PERU:
        filas_peru = _filas_hoja("7Actuals info Peru")
        for spv, col_inicio in SPV_PERU.items():
            metricas = _metricas_bloque(filas_peru, col_inicio)
            registros.extend(fila(spv, i, metricas) for i in range(len(MESES)))

    return pd.DataFrame(registros)


# =====================================================================
# Presupuesto -- hojas "Monthly 12 Budget wo Peru" y "Monthly 12 Budget Peru".
# Estructura confirmada leyendo la nota de documentación (celda A1, dejada por
# "David Eduardo Campiño Rincon"): fila 17 = título de bloque, fila 18 =
# encabezado (Month 1..12, Total 2026, Check), fila 20+ = rubros del P&L, con
# el nombre de fila en COLUMNA B (a diferencia de las hojas de Actuals, que
# usan columna C) -- son valores estáticos (snapshot congelado), no fórmulas.
#
# OJO: estas hojas NO desglosan por SPV/entidad legal (solo por Negocio /
# cliente) -- el presupuesto por SPV vive en otra hoja mucho más grande
# ("Budget ALL SPV BU Detailed", 132 bloques) que todavía no se ha mapeado.
# Por eso el presupuesto siempre se muestra "Todos los SPV", sin importar el
# filtro de País/SPV -- ver nota en la página de Budget & Goals.
# =====================================================================

# Columna 0-based donde empieza cada bloque de negocio en "Monthly 12 Budget wo Peru".
BLOQUES_PRESUPUESTO_NEGOCIO = {
    "Consolidated": 4, "NPL": 19, "Servicing": 34, "Master Service": 49,
}
COL_INICIO_PRESUPUESTO_PERU = 4  # bloque "Peru total" en "Monthly 12 Budget Peru"

FILAS_PRESUPUESTO = {
    "revenue": "Operating income", "cos": "Cost of goods sold (COGS)", "gross_profit": "Gross profit",
    "sga": "SG&A expenses", "ebitda": "EBITDA", "depreciacion": "Depreciation",
    "amortizacion": "Amortization", "operating_profit": "Operating profit", "before_tax": "Before tax profit",
    # Fila "third-party liabilities" = suma de las reservas contractuales con los 3 portafolios
    # co-invertidos (IFC/Bancoomeva/PFG) -- confirmado por triple validación cruzada: (a) el hijo
    # IFC+Bancoomeva+PFG suma exacto al padre, (b) wo-Peru + Peru reproduce EXACTO el total de la
    # hoja "Budget ALL SPV BU Detailed" (Block 10, NPL · All SPV: 18,412.9 MM), y (c) el EBITDA/
    # Adjusted EBITDA "wo Peru" de Consolidated reproduce EXACTO el par (14,653.8 / 1,409.2) que
    # ya trae el propio HTML de referencia. Mismo criterio que Actuals: Servicing/Master Service
    # publican esta fila en 0 (las reservas son 100% de NPL), NPL y Consolidated cargan el total.
    "reservas": "third-party liabilities",
}


def _metricas_bloque_presupuesto(filas: list, col_inicio: int) -> dict[str, list[float]]:
    """Extrae Ene-Jul (7 valores, columnas col_inicio..col_inicio+6) por métrica,
    buscando el texto de fila en COLUMNA B (índice 1), no C -- distinto a Actuals."""
    columnas = list(range(col_inicio, col_inicio + 7))
    return {
        clave: _serie_mensual(_fila_por_texto(filas, 1, texto), columnas)
        for clave, texto in FILAS_PRESUPUESTO.items()
    }


def _anual_bloque_presupuesto(filas: list, col_inicio: int) -> dict[str, float]:
    """Extrae 'Total 2026' (columna col_inicio+12: Month1..Month12 ocupan +0..+11, ver fila 18
    de encabezado) por métrica."""
    col_total = col_inicio + 12
    resultado = {}
    for clave, texto in FILAS_PRESUPUESTO.items():
        fila = _fila_por_texto(filas, 1, texto)
        resultado[clave] = _mm(fila[col_total]) if fila else 0.0
    return resultado


@functools.lru_cache(maxsize=128)
def cargar_presupuesto(negocio: str) -> tuple[pd.DataFrame, dict[str, float]]:
    """Presupuesto para el filtro de Negocio dado, sumando Perú cuando corresponde (mismo
    criterio que cargar_negocio() para Actuals). Devuelve (mensual Ene-Jul, anual Total 2026)."""
    filas_wo_peru = _filas_hoja("Monthly 12 Budget wo Peru")
    col_wo_peru = BLOQUES_PRESUPUESTO_NEGOCIO[negocio]
    mensual = _metricas_bloque_presupuesto(filas_wo_peru, col_wo_peru)
    anual = _anual_bloque_presupuesto(filas_wo_peru, col_wo_peru)

    if negocio in NEGOCIOS_CON_PERU:
        filas_peru = _filas_hoja("Monthly 12 Budget Peru")
        mensual_peru = _metricas_bloque_presupuesto(filas_peru, COL_INICIO_PRESUPUESTO_PERU)
        anual_peru = _anual_bloque_presupuesto(filas_peru, COL_INICIO_PRESUPUESTO_PERU)
        mensual = {k: [mensual[k][i] + mensual_peru[k][i] for i in range(len(MESES))] for k in mensual}
        anual = {k: anual[k] + anual_peru[k] for k in anual}

    mensual["ebitda_adj"] = [mensual["ebitda"][i] - mensual["reservas"][i] for i in range(len(MESES))]
    anual["ebitda_adj"] = anual["ebitda"] - anual["reservas"]

    return pd.DataFrame(mensual, index=MESES), anual


# =====================================================================
# Presupuesto por SPV/País -- hoja "Budget ALL SPV BU Detailed" (132 bloques
# apilados por fila, uno por combinación SPV × Negocio × Proyecto/campaña).
# Confirmado leyendo el catálogo completo de encabezados "BLOCK N — <SPV> |
# <Negocio>": los 132 bloques repiten EXACTAMENTE la misma plantilla de filas
# del P&L (mismo offset relativo desde el inicio del bloque para Operating
# income/COGS/Gross profit/SG&A/EBITDA/reservas), así que un solo diccionario
# de offsets sirve para cualquier bloque -- no hace falta tratarlos distinto.
#
# Validado exacto contra cargar_presupuesto(): sumar el EBITDA anual de todos
# los SPV reproduce 19,237.8 (Consolidated), 2,696.7 (Servicing), 1,132.5
# (Master Service) y 15,408.6 (NPL) -- los mismos totales ya confirmados por
# el HTML de referencia.
# =====================================================================

FILA_INICIO_PRESUPUESTO_SPV = {
    "Systemgroup SAS": {"Consolidated": 7888, "Servicing": 7999, "Master Service": 8998, "NPL": 8887},
    "Systemgroup NPL Cayman": {"Consolidated": 11218, "Servicing": 11329, "Master Service": 12217, "NPL": 12106},
    "Systemgroup Global Financial Corp": {"Consolidated": 9553, "Servicing": 9664, "Master Service": 10663, "NPL": 10552},
    "Systemgroup NPL CO SAS": {"Consolidated": 6223, "Servicing": 6334, "Master Service": 7333, "NPL": 7222},
    "Systemgroup NPL PE SAC": {"Consolidated": 4558, "Servicing": 4669, "Master Service": 5668, "NPL": 5557},
    # Sin bloque "all business units" propio en esta hoja -- para Consolidated se suman sus 3
    # bloques de Negocio (único caso especial, ver cargar_presupuesto_por_spv()).
    "Sistemgroup Internacional Peru SAC": {"Servicing": 3004, "Master Service": 4003, "NPL": 3892},
    "Systemcobro Peru SAC": {"Consolidated": 1672, "Servicing": 1783, "Master Service": 2671, "NPL": 2560},
    "Systemgroup NPL SA De CV": {"Consolidated": 12328, "Servicing": 12439, "Master Service": 13438, "NPL": 13327},
    "Systemgroup NPL HN": {"Consolidated": 13549, "Servicing": 13660, "Master Service": 14548, "NPL": 14437},
    # "Soluciones SAC" (4to SPV de Perú) no tiene bloque propio en esta hoja -- se deja en 0 más
    # abajo, mismo criterio que México/Honduras del lado Actuals (sin evidencia de presupuesto
    # separado, no se inventa un valor).
}

# Offset de fila (relativo al inicio del bloque) confirmado en el Block 1 ("All SPV | all
# business units", filas 7-117): Operating income=+2, COGS=+7, Gross profit=+36, SG&A=+38,
# EBITDA=+68, third-party liabilities (reservas contractuales)=+96.
FILAS_PRESUPUESTO_SPV_OFFSET = {
    "revenue": 2, "cos": 7, "gross_profit": 36, "sga": 38, "ebitda": 68, "reservas": 96,
}
COLS_ENE_JUL_SPV_BUDGET = list(range(4, 11))  # meses 1..7 (0-based, col E:K)


def _metricas_bloque_presupuesto_spv(filas: list, fila_inicio: int) -> dict[str, list[float]]:
    resultado = {
        clave: _serie_mensual(filas[fila_inicio + offset], COLS_ENE_JUL_SPV_BUDGET)
        for clave, offset in FILAS_PRESUPUESTO_SPV_OFFSET.items()
    }
    resultado["ebitda_adj"] = [resultado["ebitda"][i] - resultado["reservas"][i] for i in range(len(MESES))]
    return resultado


@functools.lru_cache(maxsize=128)
def cargar_presupuesto_por_spv(negocio: str) -> pd.DataFrame:
    """
    Presupuesto mensual (Ene-Jul, COP MM) desglosado por SPV/País, en formato largo (SPV, Pais,
    Mes, revenue, cos, gross_profit, sga, ebitda, reservas, ebitda_adj) -- mismo formato que
    cargar_por_spv() para Actuals, para poder reusar filtrar_por_spv_pais()/agregar_por_mes().
    """
    filas = _filas_hoja("Budget ALL SPV BU Detailed", max_row=14700)
    campos = list(FILAS_PRESUPUESTO_SPV_OFFSET) + ["ebitda_adj"]
    registros = []

    for spv, bloques_por_negocio in FILA_INICIO_PRESUPUESTO_SPV.items():
        pais = SPV_PAIS[spv]
        if negocio in bloques_por_negocio:
            metricas = _metricas_bloque_presupuesto_spv(filas, bloques_por_negocio[negocio])
        elif negocio == "Consolidated":
            # Sistemgroup Internacional Peru SAC: sin bloque "all business units" propio --
            # se suman sus 3 bloques de Negocio disponibles (Servicing+Master+NPL).
            sub = [_metricas_bloque_presupuesto_spv(filas, fi) for fi in bloques_por_negocio.values()]
            metricas = {k: [sum(m[k][i] for m in sub) for i in range(len(MESES))] for k in campos}
        else:
            metricas = {k: [0.0] * len(MESES) for k in campos}
        for i, mes in enumerate(MESES):
            registros.append({"SPV": spv, "Pais": pais, "Mes": mes, **{k: v[i] for k, v in metricas.items()}})

    campos_cero = {k: 0.0 for k in campos}
    registros.extend({"SPV": "Soluciones SAC", "Pais": "Peru", "Mes": mes, **campos_cero} for mes in MESES)

    return pd.DataFrame(registros)


def filtrar_por_spv_pais(df_spv: pd.DataFrame, paises: list[str], spvs: list[str]) -> pd.DataFrame:
    """Aplica los filtros de País y SPV sobre el DataFrame largo de cargar_por_spv()."""
    filtrado = df_spv
    if paises:
        filtrado = filtrado[filtrado["Pais"].isin(paises)]
    if spvs:
        filtrado = filtrado[filtrado["SPV"].isin(spvs)]
    return filtrado


def agregar_por_mes(df_spv_filtrado: pd.DataFrame) -> pd.DataFrame:
    """Convierte el DataFrame largo (una fila por SPV x mes) al mismo formato ancho
    (índice=mes, una columna por métrica) que devuelve cargar_negocio(), sumando
    las cifras de todos los SPV/países que hayan quedado tras el filtro."""
    columnas_metricas = [c for c in df_spv_filtrado.columns if c not in ("SPV", "Pais", "Mes")]
    if df_spv_filtrado.empty:
        return pd.DataFrame(0.0, index=MESES, columns=columnas_metricas)
    return df_spv_filtrado.groupby("Mes")[columnas_metricas].sum().reindex(MESES).fillna(0.0)
