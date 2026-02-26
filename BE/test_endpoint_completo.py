import sys
sys.path.insert(0, '.')
from app.bll.recaudo_bll import obtener_recaudo_pais_completo
from app.dal.permisos_dal import obtener_usuario_por_id

pais_name = 'ACC COL'
mes = 11
anio = 2025
id_usuario = 35

print('=== OBTENER DATOS ===')
resultado = obtener_recaudo_pais_completo(pais_name, mes, anio)
print(f'Total SIN filtrar: ${resultado["total_pais"]:,.2f}')
print(f'Subcampañas: {len(resultado["subcampanas"])}')

print('\n=== FILTRAR POR USUARIO ===')
usuario = obtener_usuario_por_id(id_usuario)
print(f'Inversionistas permitidos: {[inv["nombre_inversionista"] for inv in usuario["inversionistas"]]}')
ids_permitidos = {inv["id_inversionista"] for inv in usuario["inversionistas"]}

resultado["subcampanas"] = [
    sub for sub in resultado["subcampanas"]
    if sub.get("id_inversionista") in ids_permitidos
]

print(f'\n=== RECALCULAR ===')
resultado["total_pais"] = sum(sub.get("total", 0) for sub in resultado["subcampanas"])
resultado["cantidad_pais"] = sum(sub.get("cantidad", 0) for sub in resultado["subcampanas"])
if "total" in resultado:
    resultado["total"] = resultado["total_pais"]

print(f'Total DESPUES: ${resultado["total_pais"]:,.2f}')
print(f'Subcampañas filtradas: {len(resultado["subcampanas"])}')

print('\n=== SUBCAMPAÑAS FINALES ===')
total_manual = 0
for sub in resultado["subcampanas"]:
    print(f'{sub["nombre_campana"]}: ${sub["total"]:,.2f}')
    total_manual += sub["total"]
    
print(f'\nSUMA MANUAL: ${total_manual:,.2f}')
print(f'total_pais en resultado: ${resultado.get("total_pais", 0):,.2f}')
print(f'total en resultado: ${resultado.get("total", 0):,.2f}')
