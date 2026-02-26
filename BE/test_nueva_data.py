from app.dal.nueva_data_dal import _load_nueva_data

df = _load_nueva_data()
print("=" * 60)
print("DEBUG Nueva Data DAL")
print("=" * 60)
print(f"\nTotal rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

if "CAMPAÑA" in df.columns:
    print(f"\nUnique campaigns: {df['CAMPAÑA'].unique()}")

    for camp in df["CAMPAÑA"].unique():
        count = len(df[df["CAMPAÑA"] == camp])
        print(f"  {camp}: {count} rows")

        # Check September 2025
        sept = df[(df["CAMPAÑA"] == camp) & (df["MES"] == 9) & (df["ANIO"] == 2025)]
        if len(sept) > 0:
            total = (
                sept["VALOR_RECAUDO"].sum() if "VALOR_RECAUDO" in sept.columns else 0
            )
            print(f"    Sep 2025: {len(sept)} rows, total: ${total:,.0f}")

print("\nSample rows:")
print(df.head(3))
