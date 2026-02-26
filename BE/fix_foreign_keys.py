import pyodbc
from app.database import get_connection1

def fix_foreign_keys():
    print("=" * 60)
    print("Corrigiendo restricciones de clave foránea...")
    print("=" * 60)
    
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        # Verificar las FKs actuales
        print("\n1. Verificando restricciones actuales...")
        cursor.execute("""
            SELECT 
                fk.name AS FK_Name,
                OBJECT_NAME(fk.parent_object_id) AS Child_Table,
                OBJECT_NAME(fk.referenced_object_id) AS Parent_Table
            FROM sys.foreign_keys fk
            WHERE OBJECT_NAME(fk.parent_object_id) IN ('CampanasRolesQA', 'RolesInversionistasQA')
        """)
        
        fks = cursor.fetchall()
        for fk in fks:
            print(f"   - {fk.FK_Name}: {fk.Child_Table} -> {fk.Parent_Table}")
        
        # Intentar eliminar y recrear FK para CampanasRolesQA
        print("\n2. Corrigiendo FK de CampanasRolesQA...")
        try:
            cursor.execute("ALTER TABLE CampanasRolesQA DROP CONSTRAINT FK_CampanasRolesQA_Rol")
            print("   - Eliminada FK anterior")
        except Exception as e:
            print(f"   - No se pudo eliminar (puede que no exista): {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE CampanasRolesQA 
                ADD CONSTRAINT FK_CampanasRolesQA_RolQA 
                FOREIGN KEY (IDRol) REFERENCES RolQA(RolID)
            """)
            print("   - Creada nueva FK apuntando a RolQA")
        except Exception as e:
            print(f"   - Error al crear FK: {e}")
        
        # Intentar eliminar y recrear FK para RolesInversionistasQA
        print("\n3. Corrigiendo FK de RolesInversionistasQA...")
        try:
            cursor.execute("ALTER TABLE RolesInversionistasQA DROP CONSTRAINT FK_RolesInversionistasQA_Rol")
            print("   - Eliminada FK anterior")
        except Exception as e:
            print(f"   - No se pudo eliminar (puede que no exista): {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE RolesInversionistasQA 
                ADD CONSTRAINT FK_RolesInversionistasQA_RolQA 
                FOREIGN KEY (IDRol) REFERENCES RolQA(RolID)
            """)
            print("   - Creada nueva FK apuntando a RolQA")
        except Exception as e:
            print(f"   - Error al crear FK: {e}")
        
        conn.commit()
        
        # Verificar FKs después
        print("\n4. Verificando restricciones después de la corrección...")
        cursor.execute("""
            SELECT 
                fk.name AS FK_Name,
                OBJECT_NAME(fk.parent_object_id) AS Child_Table,
                OBJECT_NAME(fk.referenced_object_id) AS Parent_Table
            FROM sys.foreign_keys fk
            WHERE OBJECT_NAME(fk.parent_object_id) IN ('CampanasRolesQA', 'RolesInversionistasQA')
        """)
        
        fks = cursor.fetchall()
        for fk in fks:
            status = "✓ OK" if fk.Parent_Table == "RolQA" else "✗ INCORRECTO"
            print(f"   - {fk.FK_Name}: {fk.Child_Table} -> {fk.Parent_Table} {status}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Corrección completada.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nError general: {e}")
        return False

if __name__ == "__main__":
    fix_foreign_keys()
