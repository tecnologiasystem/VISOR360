import sys
sys.path.insert(0, '.')
from app.database import get_connection1

conn = get_connection1()
cursor = conn.cursor()

cursor.execute("""
    SELECT DISTINCT 
        i.IDInversionistaQA, 
        i.NombreInversionistaQA 
    FROM RolesInversionistasQA ri 
    INNER JOIN InversionistaQA i ON ri.IDInversionistaQA = i.IDInversionistaQA 
    WHERE ri.IDRol = 36 
    AND i.EsActivo = 1 
    ORDER BY i.NombreInversionistaQA
""")

rows = cursor.fetchall()
print(f'Inversionistas del rol 36 (consulta SQL directa):')
for r in rows:
    print(f'  {r.IDInversionistaQA}: {r.NombreInversionistaQA}')
print(f'\nTotal: {len(rows)}')

cursor.close()
conn.close()

print('\n=== Ahora probando obtener_usuario_por_id ===')
from app.dal.permisos_dal import obtener_usuario_por_id

usuario = obtener_usuario_por_id(35)
print(f'Inversionistas desde obtener_usuario_por_id:')
for inv in usuario['inversionistas']:
    print(f'  {inv["id_inversionista"]}: {inv["nombre_inversionista"]}')
print(f'\nTotal: {len(usuario["inversionistas"])}')
