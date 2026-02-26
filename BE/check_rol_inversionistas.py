import sys
sys.path.insert(0, '.')
from app.database import get_connection1

conn = get_connection1()
cursor = conn.cursor()

# Obtener usuario
cursor.execute("""
    SELECT u.EmailUsuarioQA, u.IDUsuarioQA, u.IDRol, r.NombreRol 
    FROM UsuariosQA u 
    INNER JOIN RolQA r ON u.IDRol = r.RolID 
    WHERE u.EmailUsuarioQA = ?
""", ('j.castillo@sgnpl.com',))
row = cursor.fetchone()
print(f'Usuario: {row.EmailUsuarioQA} (ID: {row.IDUsuarioQA})')
print(f'Rol: {row.NombreRol} (ID: {row.IDRol})')

rol_id = row.IDRol

# Obtener inversionistas del rol
cursor.execute("""
    SELECT i.IDInversionistaQA, i.NombreInversionistaQA 
    FROM RolesInversionistasQA ri 
    INNER JOIN InversionistaQA i ON ri.IDInversionistaQA = i.IDInversionistaQA 
    WHERE ri.IDRol = ?
""", (rol_id,))
invs = cursor.fetchall()
print(f'\nInversionistas asignados ({len(invs)}):')
for inv in invs:
    print(f'  - {inv.NombreInversionistaQA} (ID: {inv.IDInversionistaQA})')

cursor.close()
conn.close()
