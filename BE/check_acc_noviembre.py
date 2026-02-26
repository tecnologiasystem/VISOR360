import sys
sys.path.insert(0, '.')
from app.database import get_connection_portafolio

conn = get_connection_portafolio()
cursor = conn.cursor()

cursor.execute("""
    SELECT DISTINCT nombre_pais_portafolio, COUNT(*) as cantidad, SUM(CAST(recaudo AS DECIMAL(18,2))) as total
    FROM vw_recaudos_portafoliov2
    WHERE MONTH(fecha) = 11 AND YEAR(fecha) = 2025
    AND nombre_pais IN ('SYSTEMGROUP ACCION', 'ACC')
    GROUP BY nombre_pais_portafolio
    ORDER BY nombre_pais_portafolio
""")

rows = cursor.fetchall()
print(f'Inversionistas de ACC COL en noviembre 2025:\n')
for row in rows:
    print(f'{row.nombre_pais_portafolio}: {row.total:,.2f} ({row.cantidad} registros)')

print(f'\nTOTAL: {sum(r.total for r in rows):,.2f}')

cursor.close()
conn.close()
