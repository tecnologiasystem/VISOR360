# Script de prueba para verificar el modo híbrido
from app.dal.recaudo_dal import obtener_recaudos_por_pais_con_subcampanas

print("=" * 60)
print("PRUEBA NPL COL - Diciembre 2025")
print("=" * 60)

result = obtener_recaudos_por_pais_con_subcampanas('NPL COL', 12, 2025)
print(f"Total pais: ${result['total_pais']:,.2f}")
print(f"Fuente: {result.get('fuente', 'N/A')}")
print("\nSubcampanas:")
for s in result['subcampanas']:
    print(f"  {s['nombre_campana']}: ${s['total']:,.2f} ({s['fuente']})")

print("\n" + "=" * 60)
print("PRUEBA ACC - Diciembre 2025")
print("=" * 60)

result = obtener_recaudos_por_pais_con_subcampanas('ACC', 12, 2025)
print(f"Total pais: ${result['total_pais']:,.2f}")
print(f"Fuente: {result.get('fuente', 'N/A')}")
print("\nSubcampanas:")
for s in result['subcampanas']:
    print(f"  {s['nombre_campana']}: ${s['total']:,.2f} ({s['fuente']})")
