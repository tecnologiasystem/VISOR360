from app.database import get_connection_portafolio

conn = get_connection_portafolio()
cursor = conn.cursor()

print("=== Buscando CREDIVALORES ===")
cursor.execute("""
    SELECT DISTINCT nombre_pais_portafolio 
    FROM vw_recaudos_portafoliov2 
    WHERE nombre_pais_portafolio LIKE '%CREDIVAL%'
""")
rows = cursor.fetchall()
print("CREDIVALORES:")
for r in rows:
    print(f"  - {r.nombre_pais_portafolio}")

print("\n=== Buscando ACCION ===")
cursor.execute("""
    SELECT DISTINCT nombre_pais_portafolio 
    FROM vw_recaudos_portafoliov2 
    WHERE nombre_pais_portafolio LIKE '%ACCION%'
""")
rows = cursor.fetchall()
print("ACCION:")
for r in rows:
    print(f"  - {r.nombre_pais_portafolio}")

print("\n=== Buscando ADAMANTINE ===")
cursor.execute("""
    SELECT DISTINCT nombre_pais_portafolio 
    FROM vw_recaudos_portafoliov2 
    WHERE nombre_pais_portafolio LIKE '%ADAMANT%'
""")
rows = cursor.fetchall()
print("ADAMANTINE:")
for r in rows:
    print(f"  - {r.nombre_pais_portafolio}")

cursor.close()
conn.close()
