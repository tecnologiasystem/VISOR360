# API para gestión de metas de campañas pequeñas

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from app.dal.meta_campana_dal import (
    obtener_metas_campana_pequena,
    obtener_meta_total_pais,
    obtener_meta_campana_especifica,
    crear_meta_campana,
    eliminar_meta_campana,
)

router = APIRouter(prefix="/metas-campana", tags=["Metas Campaña"])


class MetaCampanaCreate(BaseModel):
    nombre_pais: str
    nombre_campana: str
    mes: int
    anio: int
    meta_valor: float
    usuario: Optional[str] = None
    recaudo_manual: Optional[float] = 0.0


class MetaCampanaResponse(BaseModel):
    id_meta: int
    nombre_pais: str
    nombre_campana: str
    mes: int
    anio: int
    meta_valor: float
    fecha_creacion: Optional[str]
    fecha_modificacion: Optional[str]


@router.get("/pais/{nombre_pais}")
def obtener_metas_por_pais(
    nombre_pais: str, 
    mes: int, 
    anio: int,
    id_usuario: int = Query(None, description="ID del usuario para filtrar por permisos")
):
    """
    Obtiene todas las metas de subcampañas para un país en un mes.
    Si se proporciona id_usuario, filtra solo los inversionistas permitidos.
    """
    try:
        # Normalizar nombre del país: "ACC COL" -> "ACC", "NPL PERU" -> "NPL PER"
        nombre_pais_normalizado = nombre_pais.upper().strip()
        if "ACC" in nombre_pais_normalizado and "COL" in nombre_pais_normalizado:
            nombre_pais_normalizado = "ACC"
        elif "NPL" in nombre_pais_normalizado and "PERU" in nombre_pais_normalizado:
            nombre_pais_normalizado = "NPL PER"
        
        metas = obtener_metas_campana_pequena(nombre_pais_normalizado, mes, anio)
        
        # Si hay id_usuario, filtrar por inversionistas permitidos
        if id_usuario:
            from app.dal.permisos_dal import obtener_usuario_por_id
            
            usuario = obtener_usuario_por_id(id_usuario)
            if usuario and usuario.get("inversionistas"):
                # Crear mapeo de nombres de inversionistas permitidos
                nombres_permitidos = {inv["nombre_inversionista"].upper() for inv in usuario["inversionistas"]}
                
                # Filtrar metas
                metas = [
                    meta for meta in metas
                    if meta.get("nombre_campana", "").upper() in nombres_permitidos
                ]
        
        # Recalcular total
        total = sum(meta.get("meta_valor", 0) for meta in metas)

        return {
            "nombre_pais": nombre_pais,
            "mes": mes,
            "anio": anio,
            "metas_subcampanas": metas,
            "meta_total": total,
            "cantidad_subcampanas": len(metas),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pais/{nombre_pais}/campana/{nombre_campana}")
def obtener_meta_campana(nombre_pais: str, nombre_campana: str, mes: int, anio: int):
    """
    Obtiene la meta de una subcampaña específica
    """
    try:
        meta = obtener_meta_campana_especifica(nombre_pais, nombre_campana, mes, anio)

        if meta is None:
            raise HTTPException(status_code=404, detail="Meta no encontrada")

        return {
            "nombre_pais": nombre_pais,
            "nombre_campana": nombre_campana,
            "mes": mes,
            "anio": anio,
            "meta_valor": meta,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
def crear_o_actualizar_meta(meta: MetaCampanaCreate):
    """
    Crea o actualiza una meta de subcampaña
    """
    try:
        meta_id = crear_meta_campana(
            meta.nombre_pais,
            meta.nombre_campana,
            meta.mes,
            meta.anio,
            meta.meta_valor,
            meta.usuario,
            meta.recaudo_manual,
        )

        return {
            "success": True,
            "id_meta": meta_id,
            "message": "Meta creada/actualizada correctamente",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/pais/{nombre_pais}/campana/{nombre_campana}")
def eliminar_meta(nombre_pais: str, nombre_campana: str, mes: int, anio: int):
    """
    Elimina una meta de subcampaña
    """
    try:
        eliminado = eliminar_meta_campana(nombre_pais, nombre_campana, mes, anio)

        if not eliminado:
            raise HTTPException(status_code=404, detail="Meta no encontrada")

        return {"success": True, "message": "Meta eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk")
def crear_metas_masivas(metas: List[MetaCampanaCreate]):
    """
    Crea o actualiza múltiples metas a la vez
    """
    try:
        resultados = []
        for meta in metas:
            meta_id = crear_meta_campana(
                meta.nombre_pais,
                meta.nombre_campana,
                meta.mes,
                meta.anio,
                meta.meta_valor,
                meta.usuario,
                meta.recaudo_manual,
            )
            resultados.append(
                {
                    "nombre_pais": meta.nombre_pais,
                    "nombre_campana": meta.nombre_campana,
                    "id_meta": meta_id,
                }
            )

        return {
            "success": True,
            "cantidad_procesadas": len(resultados),
            "metas": resultados,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
