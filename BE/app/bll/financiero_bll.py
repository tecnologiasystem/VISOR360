"""
BLL del modulo financiero (Dashboard Unit Economics).

Reglas de negocio entre la capa API y el DAL. NO usa SQL Server: toda la logica
de datos vive en el Excel (ver financiero_dal). Aqui se validan los filtros que
llegan del frontend y se orquesta la subida del Excel.

No se recalcula ni se duplica la logica financiera: se delega tal cual en
app.financiero.dashboard_data, que es el puente ya validado del proyecto original.
"""
from __future__ import annotations

import logging

from app.dal import financiero_dal as dal
from app.financiero import dashboard_data as dd
from app.financiero import data_loader as dl

logger = logging.getLogger(__name__)

NEGOCIOS_VALIDOS = list(dl.HOJA_POR_NEGOCIO.keys())          # Consolidated/Servicing/Master Service/NPL
MONEDAS_VALIDAS = ["COP MM", "USD MM"]
PERIODOS_VALIDOS = ["Todos", "Q1", "Q2", "Q3"] + list(dl.MESES)


def _negocio_valido(negocio: str | None) -> str:
    negocio = (negocio or "Consolidated").strip()
    return negocio if negocio in NEGOCIOS_VALIDOS else "Consolidated"


def _moneda_valida(moneda: str | None) -> str:
    moneda = (moneda or "COP MM").strip()
    return moneda if moneda in MONEDAS_VALIDAS else "COP MM"


def _periodo_valido(periodo: str | None) -> str:
    periodo = (periodo or "Todos").strip()
    return periodo if periodo in PERIODOS_VALIDOS else "Todos"


def catalogo_filtros() -> dict:
    """Valores validos para los selectores del frontend."""
    return {
        "negocios": NEGOCIOS_VALIDOS,
        "monedas": MONEDAS_VALIDAS,
        "periodos": PERIODOS_VALIDOS,
        "meses": list(dl.MESES),
    }


def snapshot(negocio: str | None = None, moneda: str | None = None,
             periodo: str | None = None, paises: list[str] | None = None,
             spvs: list[str] | None = None) -> dict:
    """Snapshot para la pestana Business Unit (delega en dashboard_data)."""
    return dd.construir_snapshot(
        negocio=_negocio_valido(negocio),
        moneda=_moneda_valida(moneda),
        periodo=_periodo_valido(periodo),
        paises=paises or None,
        spvs=spvs or None,
    )


def performance(negocio: str | None = None) -> dict:
    """Datos de la pestana Performance (delega en dashboard_data)."""
    return dd.construir_performance(_negocio_valido(negocio))


def budget(negocio: str | None = None) -> dict:
    """Datos de la pestana Budget & Goals (delega en dashboard_data)."""
    return dd.construir_budget(_negocio_valido(negocio))


def estado_excel() -> dict:
    """Metadatos del Excel vigente para la UI."""
    return dal.info_excel()


def reemplazar_excel(nombre_archivo: str, contenido: bytes) -> dict:
    """Valida y reemplaza el Excel vigente.

    Devuelve un dict con el resultado y mensajes ya listos para la UI.
    """
    if not nombre_archivo.lower().endswith((".xlsx", ".xlsm")):
        return {"ok": False, "mensaje": "El archivo debe ser .xlsx o .xlsm.",
                "faltantes": [], "backup": None}
    if not contenido:
        return {"ok": False, "mensaje": "El archivo llego vacio.",
                "faltantes": [], "backup": None}

    resultado = dal.reemplazar_excel(contenido)
    if resultado.get("error"):
        return {"ok": False, "mensaje": f"No se pudo leer el Excel: {resultado['error']}",
                "faltantes": [], "backup": None}
    if resultado.get("faltantes"):
        faltan = ", ".join(resultado["faltantes"])
        return {
            "ok": False,
            "mensaje": f"El archivo no se cargo: le faltan hojas requeridas ({faltan}). "
                       "El Excel vigente no se toco.",
            "faltantes": resultado["faltantes"], "backup": None,
        }
    return {
        "ok": True,
        "mensaje": f"Excel actualizado correctamente. Respaldo del anterior: {resultado['backup']}.",
        "faltantes": [], "backup": resultado.get("backup"),
    }
