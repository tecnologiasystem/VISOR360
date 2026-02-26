from app.database import get_connection

def obtener_todas_las_marcaciones():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM marcacion")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows
