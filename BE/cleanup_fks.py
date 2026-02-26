import pyodbc
from app.database import get_connection1

def cleanup_old_fks():
    print("Limpiando FKs antiguas...")
    
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        # Intentar eliminar la FK antigua que apunta a Rol (no RolQA)
        try:
            cursor.execute("ALTER TABLE CampanasRolesQA DROP CONSTRAINT FK_CampanasRolesQA_Rol")
            print("Eliminada FK_CampanasRolesQA_Rol")
            conn.commit()
        except Exception as e:
            print(f"No se pudo eliminar FK_CampanasRolesQA_Rol: {e}")
        
        # Verificar estado final
        print("\nEstado final de las FKs:")
        cursor.execute("""
            SELECT 
                fk.name AS FK_Name,
                OBJECT_NAME(fk.parent_object_id) AS Child_Table,
                OBJECT_NAME(fk.referenced_object_id) AS Parent_Table
            FROM sys.foreign_keys fk
            WHERE OBJECT_NAME(fk.parent_object_id) IN ('CampanasRolesQA', 'RolesInversionistasQA')
        """)
        
        for fk in cursor.fetchall():
            status = "✓" if fk.Parent_Table in ["RolQA", "CampanasQA", "InversionistaQA"] else "✗"
            print(f"   {status} {fk.FK_Name}: {fk.Child_Table} -> {fk.Parent_Table}")
        
        cursor.close()
        conn.close()
        print("\nListo!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cleanup_old_fks()
