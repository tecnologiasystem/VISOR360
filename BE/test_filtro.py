import sys
sys.path.insert(0, '.')
from app.bll.recaudo_bll import obtener_recaudo_pais_completo
from app.dal.permisos_dal import obtener_usuario_por_id

# Simular el proceso completo del endpoint
pais_name = 'ACC COL'
mes = 11  # noviembre
anio = 2025
id_usuario = 35

print('=== PASO 1: Obtener datos sin filtrar ===')
resultado = obtener_recaudo_pais_completo(pais_name, mes, anio)
print(f'Total ANTES de filtrar: ${resultado["total_pais"]:,.2f}')
print(f'Subcampañas ANTES: {len(resultado["subcampanas"])}')

print('\n=== PASO 2: Filtrar por usuario ===')
usuario = obtener_usuario_por_id(id_usuario)
print(f'Inversionistas permitidos: {[inv["nombre_inversionista"] for inv in usuario["inversionistas"]]}')
ids_permitidos = {inv['id_inversionista'] for inv in usuario['inversionistas']}
print(f'IDs permitidos: {ids_permitidos}')

resultado['subcampanas'] = [
    sub for sub in resultado['subcampanas']
    if sub.get('id_inversionista') in ids_permitidos
]
print(f'Subcampañas DESPUES: {len(resultado["subcampanas"])}')

print('\n=== PASO 3: Recalcular total ===')
resultado['total_pais'] = sum(sub.get('total', 0) for sub in resultado['subcampanas'])
resultado['cantidad_pais'] = sum(sub.get('cantidad', 0) for sub in resultado['subcampanas'])
print(f'Total DESPUES de filtrar: ${resultado["total_pais"]:,.2f}')

print('\n=== SUBCAMPAÑAS FINALES ===')
for sub in resultado['subcampanas']:
    print(f'  {sub["nombre_campana"]}: ${sub["total"]:,.2f} (ID: {sub.get("id_inversionista")})')
