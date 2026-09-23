"""Contrato de datos para una interfaz web del dashboard.

Mantiene la capa visual separada de los cálculos de ``data_loader``. La futura
interfaz HTML puede consumir ``construir_snapshot`` sin leer el Excel ni repetir
las reglas financieras.
"""
from __future__ import annotations

from typing import Any

from app.financiero import data_loader as dl


def _serie(df, columna: str) -> list[dict[str, float | str]]:
    return [
        {"mes": str(mes), "valor": round(float(valor), 4)}
        for mes, valor in df[columna].items()
    ]


def construir_snapshot(
    negocio: str = "Consolidated",
    moneda: str = "COP MM",
    periodo: str = "Todos",
    paises: list[str] | None = None,
    spvs: list[str] | None = None,
) -> dict[str, Any]:
    """Devuelve datos serializables para el dashboard visual.

    Los filtros de país/SPV se aplican sobre las mismas funciones que usa
    Streamlit. ``paises`` y ``spvs`` vacíos significan todos los valores.
    """
    df_spv = dl.cargar_por_spv(negocio)
    paises_disponibles = sorted(df_spv["Pais"].unique().tolist())
    paises_sel = paises if paises else paises_disponibles
    spvs_disponibles = sorted(
        df_spv.loc[df_spv["Pais"].isin(paises_sel), "SPV"].unique().tolist()
    )
    spvs_sel = spvs if spvs else spvs_disponibles

    if set(paises_sel) != set(paises_disponibles) or set(spvs_sel) != set(spvs_disponibles):
        df = dl.agregar_por_mes(dl.filtrar_por_spv_pais(df_spv, paises_sel, spvs_sel))
        alcance = f"{', '.join(paises_sel) or 'Ningún país'} · {len(spvs_sel)} SPV"
    else:
        df = dl.cargar_negocio(negocio)
        alcance = "All SPV /w Peru"

    df = dl.filtrar_periodo(df, periodo or "Todos")
    df = dl.convertir_moneda(df, moneda or "COP MM")

    presupuesto_mensual, presupuesto_anual = dl.cargar_presupuesto(negocio)
    presupuesto_mensual = dl.convertir_moneda(presupuesto_mensual, moneda or "COP MM")

    kpis = {}
    for columna in ("revenue", "gross_profit", "ebitda", "ebitda_adj", "operating_profit", "net_before_reservas"):
        kpis[columna] = round(float(df[columna].sum()), 4)
    kpis["gross_margin_pct"] = round(kpis["gross_profit"] / kpis["revenue"] * 100, 4) if kpis["revenue"] else 0
    kpis["ebitda_margin_pct"] = round(kpis["ebitda"] / kpis["revenue"] * 100, 4) if kpis["revenue"] else 0

    detalle = []
    for clave, etiqueta in (
        ("revenue", "Operating income"), ("cos", "Cost of goods sold (COGS)"),
        ("gross_profit", "Gross profit"), ("sga", "SG&A expenses"),
        ("ebitda", "EBITDA"), ("reservas", "Reserves"),
        ("ebitda_adj", "Adjusted EBITDA"), ("operating_profit", "Operating profit"),
        ("net_before_reservas", "Net income before reserves"),
    ):
        detalle.append({"linea": etiqueta, "serie": _serie(df, clave), "ytd": round(float(df[clave].sum()), 4)})

    revenue_contrato = dl.cargar_revenue_por_contrato(negocio)
    contratos = []
    if revenue_contrato is not None and not revenue_contrato.empty:
        contratos = [
            {"contrato": str(row["Contrato"]), "revenue_ytd": round(float(row["Revenue YTD (MM)"]), 4)}
            for _, row in revenue_contrato.iterrows()
        ]

    return {
        "negocio": negocio,
        "moneda": moneda,
        "periodo": periodo or "Todos",
        "alcance": alcance,
        "catalogos": {
            "negocios": list(dl.HOJA_POR_NEGOCIO),
            "paises": paises_disponibles,
            "spvs": spvs_disponibles,
            "meses": list(dl.MESES),
        },
        "kpis": kpis,
        "series": {
            "revenue": _serie(df, "revenue"),
            "gross_profit": _serie(df, "gross_profit"),
            "ebitda": _serie(df, "ebitda"),
            "ebitda_adj": _serie(df, "ebitda_adj"),
        },
        "budget": {
            "revenue_ytd": round(float(presupuesto_mensual["revenue"].sum()), 4),
            "ebitda_ytd": round(float(presupuesto_mensual["ebitda"].sum()), 4),
            "revenue_annual": round(float(presupuesto_anual["revenue"]), 4),
            "ebitda_annual": round(float(presupuesto_anual["ebitda"]), 4),
        },
        "detalle": detalle,
        "contratos": contratos,
    }


def construir_performance(negocio: str = "Consolidated") -> dict[str, Any]:
    """Datos resumidos para la vista Performance."""
    composicion = dl.cargar_composicion_costos(negocio)
    terceros = dl.cargar_top_terceros(top_n=15)
    crxm = dl.cargar_crxm(negocio)
    return {
        "negocio": negocio,
        "composicion": composicion.fillna(0).to_dict(orient="records"),
        "terceros": terceros.fillna(0).to_dict(orient="records"),
        "crxm": crxm.fillna(0).to_dict(orient="records") if crxm is not None else [],
    }


def construir_budget(negocio: str = "Consolidated") -> dict[str, Any]:
    """Datos de presupuesto anual y YTD para la vista Budget & Goals."""
    mensual, anual = dl.cargar_presupuesto(negocio)
    return {
        "negocio": negocio,
        "mensual": mensual.fillna(0).to_dict(orient="index"),
        "anual": {clave: round(float(valor), 4) for clave, valor in anual.items()},
    }