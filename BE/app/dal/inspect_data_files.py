import os
import glob
import pandas as pd

repo_root = os.path.dirname(os.path.dirname(__file__))
be_root = os.path.dirname(repo_root)
data_dir = os.path.join(be_root, 'DATA')
print('DATA folder:', data_dir)
patterns = ['*.xlsx', '*.xls', '*.csv']
files = []
for pat in patterns:
    files.extend(glob.glob(os.path.join(data_dir, pat)))

if not files:
    print('No files found in DATA')
    raise SystemExit(0)

for f in sorted(files):
    print('\n---', os.path.basename(f), '---')
    try:
        if f.lower().endswith('.csv'):
            df = pd.read_csv(f, nrows=5)
            df_full = pd.read_csv(f)
        else:
            df = pd.read_excel(f, nrows=5)
            df_full = pd.read_excel(f)
    except Exception as e:
        print('Error reading file:', e)
        continue
    cols = [str(c).strip() for c in df.columns]
    print('Columns:', cols)
    print('Preview rows:')
    print(df.head().to_string(index=False))

    # Show sample unique values for likely important columns
    lower_cols = [c.lower() for c in cols]
    want = []
    for candidate in ['pais', 'inversionista', 'valor', 'monto', 'fecha', 'campana', 'nombre_campana', 'subcampana']:
        for i,c in enumerate(lower_cols):
            if candidate in c:
                want.append(cols[i])
                break

    for col in want:
        try:
            series = df_full[col].astype(str).str.strip()
            uniques = series.dropna().unique()[:10]
            print(f"Sample values for '{col}':", uniques.tolist())
        except Exception:
            pass

print('\nInspection finished')
