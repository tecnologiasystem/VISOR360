

# Importamos la función que va a traer los datos de la base (DAL)
from app.dal.embudo_dal import get_embudo_top1000

def listar_embudo():
    """
    Esta función obtiene los datos de la base de datos y hace cálculos adicionales.
    """
    # 1️⃣ Llamamos a la DAL para que nos traiga los datos
    datos = get_embudo_top1000()  
    
    # 2️⃣ Recorremos cada registro (cada página del libro)
    for registro in datos:
        # Agregamos un nuevo campo llamado 'saldo_total'
        # que es la suma de 'saldo_capital' + 'saldo_capital_consolidado'
        registro['saldo_total'] = registro['saldo_capital'] + registro['saldo_capital_consolidado']
    
    # 3️⃣ Devolvemos los datos listos
    return datos
