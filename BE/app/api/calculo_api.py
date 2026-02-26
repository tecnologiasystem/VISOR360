from fastapi import APIRouter
from app.bll.calculo_bll import CalculoBLL

router = APIRouter(prefix="/calculo", tags=["Calculo"])

@router.get("/recaudo/por-dia")
def obtener_recaudo_por_dia(
    campana: str = None,
    mes: int = None,
    dia_corte: int = None,
    year: int = None
):
    return CalculoBLL.buscar_recaudo_por_dia(
        campana=campana,
        mes=mes,
        dia_corte=dia_corte,
        year=year
    )


@router.get("/recaudo/por-mes")
def obtener_recaudo_por_mes(
    campana: str = None,
    mes: int = None,
    year: int = None
):
    return CalculoBLL.buscar_recaudo_por_mes(
        campana=campana,
        mes=mes,
        year=year
    )


@router.get("/recaudo/ultimos-4-meses")
def obtener_recaudo_ultimos_4_meses(
    campana: str = None,
    year: int = None
):
    return CalculoBLL.buscar_recaudo_ultimos_4_meses(
        campana=campana,
        year=year
    )




