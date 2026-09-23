"""
API del modulo financiero (Dashboard Unit Economics).

Expone las 3 vistas del tablero (Business Unit, Performance, Budget & Goals)
y la carga del Excel fuente. NO usa SQL Server: los datos salen del Excel que
persiste en BE/datos/ (ver app/dal/financiero_dal.py).

Contrato (montado bajo /api por main.py):
    GET  /api/financiero/snapshot?negocio=&moneda=&periodo=&pais=&spv=
    GET  /api/financiero/performance?negocio=
    GET  /api/financiero/budget?negocio=
    GET  /api/financiero/catalogo
    GET  /api/financiero/excel          -> metadatos del Excel vigente
    POST /api/financiero/upload-excel   -> reemplaza el Excel (multipart)
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.bll import financiero_bll as bll

router = APIRouter(prefix="/financiero", tags=["Financiero · Unit Economics"])


@router.get("/catalogo")
def get_catalogo():
    """Valores validos para los selectores del frontend."""
    try:
        return {"success": True, "data": bll.catalogo_filtros(),
                "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/excel")
def get_excel():
    """Metadatos del Excel vigente (nombre, ubicacion, fecha de actualizacion)."""
    try:
        return {"success": True, "data": bll.estado_excel(),
                "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snapshot")
def get_snapshot(
    negocio: str = Query("Consolidated", description="Consolidated, Servicing, Master Service o NPL"),
    moneda: str = Query("COP MM", description="COP MM o USD MM"),
    periodo: str = Query("Todos", description="Todos, Q1..Q3 o un mes (Ene..Jul)"),
    pais: list[str] = Query(default=[], description="Paises seleccionados (repetible)"),
    spv: list[str] = Query(default=[], description="SPV seleccionados (repetible)"),
):
    """Snapshot de la vista Business Unit (KPIs, series, detalle, contratos, budget)."""
    try:
        datos = bll.snapshot(negocio=negocio, moneda=moneda, periodo=periodo,
                             paises=pais, spvs=spv)
        return {"success": True, "data": datos, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
def get_performance(negocio: str = Query("Consolidated")):
    """Vista Performance: composicion de costos, top terceros y CRxM."""
    try:
        return {"success": True, "data": bll.performance(negocio),
                "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget")
def get_budget(negocio: str = Query("Consolidated")):
    """Vista Budget & Goals: presupuesto mensual y anual."""
    try:
        return {"success": True, "data": bll.budget(negocio),
                "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-excel")
async def post_upload_excel(archivo: UploadFile = File(...)):
    """Reemplaza el Excel fuente.

    Valida que el archivo traiga las 12 hojas requeridas ANTES de tocar el vigente;
    si es valido, respalda el anterior con fecha y lo reemplaza. Las vistas se
    recalculan solas (se limpia la cache en memoria).
    """
    try:
        contenido = await archivo.read()
        resultado = bll.reemplazar_excel(archivo.filename or "", contenido)
        if not resultado["ok"]:
            raise HTTPException(status_code=400, detail=resultado["mensaje"])
        return {
            "success": True,
            "data": resultado,
            "message": resultado["mensaje"],
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
