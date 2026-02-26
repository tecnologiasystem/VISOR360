import sys
sys.path.insert(0, '.')
from app.dal.meta_campana_dal import obtener_metas_campana_pequena
from app.dal.permisos_dal import obtener_usuario_por_id

# Obtener metas sin filtrar
metas = obtener_metas_campana_pequena('ACC', 12, 2025)
print(f'Metas de ACC diciembre (sin filtrar): {len(metas)}')
for meta in metas:
    print(f'  - {meta["nombre_campana"]}: ${meta["meta_valor"]:,.0f}')

# Obtener inversionistas del usuario
usuario = obtener_usuario_por_id(35)
nombres_permitidos = {inv["nombre_inversionista"].upper() for inv in usuario["inversionistas"]}
print(f'\nInversionistas permitidos:')
for nombre in sorted(nombres_permitidos):
    print(f'  - {nombre}')

# Filtrar
metas_filtradas = [
    meta for meta in metas
    if meta.get("nombre_campana", "").upper() in nombres_permitidos
]

print(f'\nMetas filtradas: {len(metas_filtradas)}')
for meta in metas_filtradas:
    print(f'  - {meta["nombre_campana"]}: ${meta["meta_valor"]:,.0f}')
    
print(f'\nComparaciones:')
for meta in metas:
    nombre_meta = meta.get("nombre_campana", "").upper()
    esta = nombre_meta in nombres_permitidos
    print(f'  "{nombre_meta}" in nombres_permitidos? {esta}')
