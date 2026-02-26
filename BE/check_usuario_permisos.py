import sys
sys.path.insert(0, '.')
from app.dal.permisos_dal import obtener_usuario_por_id

id_usuario = 35

usuario = obtener_usuario_por_id(id_usuario)
print(f"Usuario ID {id_usuario}:")
print(f"  Email: {usuario['email']}")
print(f"  Rol: {usuario['nombre_rol']}")
print(f"\nCampañas ({len(usuario['campanas'])}):")
for c in usuario['campanas']:
    print(f"  - {c['nombre']} (ID: {c['id']})")
    
print(f"\nInversionistas ({len(usuario['inversionistas'])}):")
for i in usuario['inversionistas']:
    print(f"  - {i['nombre_inversionista']} (ID: {i['id_inversionista']})")

print(f"\nIDs de inversionistas permitidos: {[i['id_inversionista'] for i in usuario['inversionistas']]}")
