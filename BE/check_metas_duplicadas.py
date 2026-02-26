import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=172.18.72.111;"
    "DATABASE=LOGS;"
    "UID=NEXUM;"
    "PWD=REDACTED_ROTATE_THIS_PASSWORD;"
    "TrustServerCertificate=yes;"
    "Encrypt=no;"
)
cursor = conn.cursor()

print("=" * 80)
print("METAS DICIEMBRE 2025 - NPL COL")
print("=" * 80)
cursor.execute("""
    SELECT nombre_campana_pequena, meta_valor 
    FROM metas_campana_pequena 
    WHERE nombre_pais = 'NPL COL' 
    AND mes = 12 
    AND anio = 2025 
    ORDER BY nombre_campana_pequena
""")
rows = cursor.fetchall()
total_dic = 0
for row in rows:
    print(f"{row[0]:<20} ${row[1]:>15,.2f}")
    total_dic += row[1]
print("=" * 80)
print(f"{'TOTAL DICIEMBRE':<20} ${total_dic:>15,.2f}")
print()

print("=" * 80)
print("METAS ENERO 2026 - NPL COL")
print("=" * 80)
cursor.execute("""
    SELECT nombre_campana_pequena, meta_valor 
    FROM metas_campana_pequena 
    WHERE nombre_pais = 'NPL COL' 
    AND mes = 1 
    AND anio = 2026 
    ORDER BY nombre_campana_pequena
""")
rows = cursor.fetchall()
total_ene = 0
for row in rows:
    print(f"{row[0]:<20} ${row[1]:>15,.2f}")
    total_ene += row[1]
print("=" * 80)
print(f"{'TOTAL ENERO':<20} ${total_ene:>15,.2f}")

cursor.close()
conn.close()

print()
print(f"Diferencia: ${total_dic - total_ene:,.2f}")
