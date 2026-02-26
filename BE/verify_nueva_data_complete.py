import pandas as pd

df = pd.read_excel("DATA/Nueva Data.xlsx", sheet_name="Final")

print("=" * 60)
print("DATOS COMPLETOS EN NUEVA DATA.XLSX")
print("=" * 60)

for campana in ["NPL", "ACC", "Peru", "Chile"]:
    print(f"\n{campana}:")
    data = df[df["Campaña"] == campana]

    if len(data) == 0:
        print(f"  NO HAY DATOS")
        continue

    # Agrupar por año-mes
    for ano_mes in data["AÑO_MES"].unique():
        mes_data = data[data["AÑO_MES"] == ano_mes]
        total_recaudo = mes_data[" VALOR RECAUDO "].sum()
        total_meta = mes_data["Meta"].sum()

        print(f"  {ano_mes}:")
        print(f"    Recaudo Total: ${total_recaudo:,.0f}")
        print(f"    Meta Total: ${total_meta:,.0f}")
        print(f"    Por inversionista:")
        for inv in mes_data["INVERSIONISTA"].unique():
            inv_data = mes_data[mes_data["INVERSIONISTA"] == inv]
            rec = inv_data[" VALOR RECAUDO "].sum()
            met = inv_data["Meta"].sum()
            print(f"      {inv}: Recaudo=${rec:,.0f}, Meta=${met:,.0f}")
