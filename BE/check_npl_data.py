import pandas as pd

df = pd.read_excel("DATA/Nueva Data.xlsx", sheet_name="Final")

print("Data count by campaign:")
print(df.groupby("Campaña").size())

print("\n\nNPL data:")
npl = df[df["Campaña"] == "NPL"]
print(f"Total NPL rows: {len(npl)}")

if len(npl) > 0:
    print("\nSample NPL data:")
    print(npl[["Campaña", "AÑO_MES", " VALOR RECAUDO ", "INVERSIONISTA"]].head(10))
    print(f"\nTotal VALOR RECAUDO for NPL: {npl[' VALOR RECAUDO '].sum():,.0f}")
