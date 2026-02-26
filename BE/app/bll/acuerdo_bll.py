from app.dal.acuerdo_dal import obtener_todos_los_acuerdos

def listar_acuerdos():
    # Aquí podrías agregar validaciones o filtros en el futuro
    return obtener_todos_los_acuerdos()
