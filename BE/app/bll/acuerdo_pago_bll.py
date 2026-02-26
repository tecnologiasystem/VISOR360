from app.dal.acuerdo_pago_dal import obtener_todos_los_acuerdos_pago

def listar_acuerdos_pago():
    """
    Llama al DAL y retorna la lista de acuerdos de pago.
    Aquí podríamos aplicar reglas o filtros si hiciera falta.
    """
    datos = obtener_todos_los_acuerdos_pago()
    return datos
