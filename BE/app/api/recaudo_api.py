from fastapi import APIRouter, Query, HTTPException
from app.bll.recaudo_bll import (
    listar_recaudos,
    obtener_recaudo_por_campana_mes,
    obtener_recaudo_pais_completo,
    obtener_recaudo_diario,
)

router = APIRouter(prefix="/recaudos", tags=["Recaudos"])


@router.get("/")
def obtener_recaudos():
    """
    Endpoint que devuelve todos los recaudos.
    Llama a la capa BLL y retorna la lista de datos.
    """
    return listar_recaudos()


@router.get("/campana/{nombre_campana}")
def obtener_recaudo_campana(
    nombre_campana: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
    hasta_hoy: bool = Query(
        False, description="Si es true, solo cuenta hasta el día actual"
    ),
):
    """
    Obtiene el recaudo total de una campaña en un mes específico usando el nombre de la campaña.
    Si hasta_hoy=true, solo suma recaudos hasta la fecha actual.
    """
    return obtener_recaudo_por_campana_mes(nombre_campana, mes, anio, hasta_hoy)


@router.get("/pais/{id_pais}")
def obtener_recaudo_por_pais(
    id_pais: int,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
    id_usuario: int = Query(None, description="ID del usuario para filtrar por permisos"),
):
    """
    Obtiene el recaudo de un país (campaña grande) incluyendo el desglose por subcampañas.
    Si se proporciona id_usuario, filtra solo los inversionistas permitidos para ese usuario.
    """
    try:
        resultado = obtener_recaudo_pais_completo(id_pais, mes, anio)
        
        # Si hay id_usuario, filtrar por inversionistas permitidos
        if id_usuario:
            from app.dal.permisos_dal import obtener_usuario_por_id
            
            # Obtener inversionistas permitidos directamente del usuario
            usuario = obtener_usuario_por_id(id_usuario)
            if usuario and usuario.get("inversionistas"):
                ids_permitidos = {inv["id_inversionista"] for inv in usuario["inversionistas"]}
                
                # Filtrar subcampañas
                if "subcampanas" in resultado:
                    resultado["subcampanas"] = [
                        sub for sub in resultado["subcampanas"]
                        if sub.get("id_inversionista") in ids_permitidos
                    ]
                    
                    # Recalcular el total
                    resultado["total"] = sum(sub.get("total", 0) for sub in resultado["subcampanas"])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pais/{id_pais}/diario")
def obtener_recaudo_diario_endpoint(
    id_pais: int,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
):
    """
    Obtiene el recaudo agrupado por día de un país en un mes específico.
    Útil para mostrar el scroll de recaudos diarios.
    """
    try:
        return obtener_recaudo_diario(id_pais, mes, anio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pais_by_name/{pais_name}")
def obtener_recaudo_por_pais_name(
    pais_name: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
    id_usuario: int = Query(None, description="ID del usuario para filtrar por permisos"),
):
    """Endpoint que acepta el nombre del pais (por ejemplo 'NPL COL') en lugar de id.
    Si se proporciona id_usuario, filtra solo los inversionistas permitidos para ese usuario.
    """
    try:
        resultado = obtener_recaudo_pais_completo(pais_name, mes, anio)
        
        # Si hay id_usuario, filtrar por inversionistas permitidos
        if id_usuario:
            from app.dal.permisos_dal import obtener_usuario_por_id
            
            # Obtener inversionistas permitidos directamente del usuario
            usuario = obtener_usuario_por_id(id_usuario)
            if usuario and usuario.get("inversionistas"):
                ids_permitidos = {inv["id_inversionista"] for inv in usuario["inversionistas"]}
                
                # Filtrar subcampañas
                if "subcampanas" in resultado:
                    resultado["subcampanas"] = [
                        sub for sub in resultado["subcampanas"]
                        if sub.get("id_inversionista") in ids_permitidos
                    ]
                    
                    # Recalcular el total_pais y cantidad_pais
                    nuevo_total = sum(sub.get("total", 0) for sub in resultado["subcampanas"])
                    nueva_cantidad = sum(sub.get("cantidad", 0) for sub in resultado["subcampanas"])
                    
                    resultado["total_pais"] = nuevo_total
                    resultado["cantidad_pais"] = nueva_cantidad
                    resultado["total"] = nuevo_total  # Para compatibilidad
                    resultado["cantidad"] = nueva_cantidad  # Para compatibilidad
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pais_by_name/{pais_name}/diario")
def obtener_recaudo_diario_por_pais_name(
    pais_name: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
):
    try:
        return obtener_recaudo_diario(pais_name, mes, anio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pais_by_name/{pais_name}/campanas")
def obtener_campanas_por_pais_name(
    pais_name: str,
    mes: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    anio: int = Query(..., ge=2000, description="Año"),
):
    """Devuelve la lista (y opcionalmente totales por subcampaña) para un país identificado por nombre.
    Si el BLL/ DAL están en modo Excel, intentará leer subcampañas desde los Excel.
    """
    try:
        # Reuse the BLL function that builds the country + subcampaign breakdown
        result = obtener_recaudo_pais_completo(pais_name, mes, anio)
        # If the BLL returned a full structure, extract subcampanas
        if isinstance(result, dict) and "subcampanas" in result:
            return result["subcampanas"]
        # Otherwise, try calling the DAL directly (fallback)
        from app.dal import recaudo_dal

        campanas = recaudo_dal.obtener_campanas_de_pais(pais_name)
        return campanas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
