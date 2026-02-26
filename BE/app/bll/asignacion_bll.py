
from app.dal.embudo_dal import get_embudo_top1000

def listar_asignaciones():
    
    datos = get_embudo_top1000()  
    

    return datos                                  