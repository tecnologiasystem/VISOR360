# API para Metas
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.bll.meta_bll import MetaBLL

router = APIRouter(prefix="/metas", tags=["Metas"])

class MetaCreate(BaseModel):
    id_pais: int
    id_campana: Optional[int] = None
    mes: int
    anio: int
    monto_meta: float
    usuario_creacion: Optional[int] = None

class MetaUpdate(BaseModel):
    monto_meta: float

@router.get("/paises")
def listar_paises():
    """
    Obtiene la lista de países (campañas grandes)
    """
    try:
        return MetaBLL.listar_paises()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pais/{id_pais}")
def obtener_metas_pais(
    id_pais: int,
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2020)
):
    """
    Obtiene todas las metas de un país (general + subcampañas) para un mes/año
    """
    try:
        return MetaBLL.obtener_metas_mes(id_pais, mes, anio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pais/{id_pais}/general")
def obtener_meta_general(
    id_pais: int,
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2020)
):
    """
    Obtiene solo la meta general del país (sin subcampañas)
    """
    try:
        monto = MetaBLL.obtener_meta_pais(id_pais, mes, anio)
        return {"monto_meta": monto}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_meta(meta: MetaCreate):
    """
    Crea una nueva meta
    """
    try:
        id_meta = MetaBLL.crear_nueva_meta(
            meta.id_pais,
            meta.mes,
            meta.anio,
            meta.monto_meta,
            meta.id_campana,
            meta.usuario_creacion
        )
        return {"message": "Meta creada exitosamente", "id_meta": id_meta}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id_meta}")
def actualizar_meta(id_meta: int, meta: MetaUpdate):
    """
    Actualiza el monto de una meta existente
    """
    try:
        MetaBLL.modificar_meta(id_meta, meta.monto_meta)
        return {"message": "Meta actualizada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_meta}")
def eliminar_meta(id_meta: int):
    """
    Elimina una meta
    """
    try:
        MetaBLL.borrar_meta(id_meta)
        return {"message": "Meta eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
