from app.dal.marcacion_dal import obtener_todas_las_marcaciones

def listar_marcaciones():
    """
    Lógica de negocio: obtiene las marcaciones desde la capa DAL.
    """
    return obtener_todas_las_marcaciones()
