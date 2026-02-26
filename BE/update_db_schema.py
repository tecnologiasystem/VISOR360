import pyodbc
from app.database import get_connection1

def update_schema():
    print("Iniciando actualización del esquema de base de datos...")
    
    try:
        conn = get_connection1()
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen para evitar errores
        cursor.execute("SELECT TOP 1 * FROM RolQA")
        columns = [column[0] for column in cursor.description]
        
        # Agregar GestionMetas si no existe
        if 'GestionMetas' not in columns:
            print("Agregando columna GestionMetas...")
            cursor.execute("ALTER TABLE RolQA ADD GestionMetas BIT NOT NULL DEFAULT 0")
            print("Columna GestionMetas agregada.")
        else:
            print("La columna GestionMetas ya existe.")
            
        # Agregar GestionUsuarios si no existe
        if 'GestionUsuarios' not in columns:
            print("Agregando columna GestionUsuarios...")
            cursor.execute("ALTER TABLE RolQA ADD GestionUsuarios BIT NOT NULL DEFAULT 0")
            print("Columna GestionUsuarios agregada.")
        else:
            print("La columna GestionUsuarios ya existe.")
            
        conn.commit()
        cursor.close()
        conn.close()
        print("Actualización de esquema completada exitosamente.")
        return True
        
    except Exception as e:
        print(f"Error al actualizar el esquema: {e}")
        return False

if __name__ == "__main__":
    update_schema()
