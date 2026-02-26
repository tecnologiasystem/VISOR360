import sys
sys.path.insert(0, '.')
from app.dal.meta_campana_dal import obtener_metas_campana_pequena

# Ver metas de ACC COL diciembre SIN filtrar
metas = obtener_metas_campana_pequena('ACC COL', 12, 2025)
print(f'Metas de ACC COL - Diciembre 2025 (SIN filtrar):')
print(f'Total de metas: {len(metas)}')
for meta in metas:
    print(f'  - {meta.get("nombre_campana")}: ${meta.get("meta_valor"):,.2f}')

print(f'\nTotal suma: ${sum(m.get("meta_valor", 0) for m in metas):,.2f}')
