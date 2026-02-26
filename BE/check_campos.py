import sys
sys.path.insert(0, '.')
from app.bll.recaudo_bll import obtener_recaudo_pais_completo

r = obtener_recaudo_pais_completo('ACC COL', 11, 2025)
print(f'Campos en resultado:')
print(f'  total: {r.get("total")}')
print(f'  total_pais: {r.get("total_pais")}')
print(f'  cantidad: {r.get("cantidad")}')
print(f'  cantidad_pais: {r.get("cantidad_pais")}')
