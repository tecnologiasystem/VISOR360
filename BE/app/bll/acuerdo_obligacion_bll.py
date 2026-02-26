from app.dal.acuerdo_obligacion_dal import obtener_todos_los_acuerdos_obligacion

def listar_acuerdos_obligacion():
   
    datos = obtener_todos_los_acuerdos_obligacion()
    return datos