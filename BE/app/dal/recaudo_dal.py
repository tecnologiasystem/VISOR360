from app.database import get_connection, get_campana_bd_name, campana_tiene_datos_en_bd
from app.utils.dias_habiles import obtener_dias_habiles_mes
from typing import List, Dict
import os
import glob
import json

# ===================== CONFIGURACIÓN DE MODO HÍBRIDO =====================
# READ_FROM_EXCEL: Si True, usa Excel como fuente primaria (modo legacy)
# USE_HYBRID_MODE: Si True, intenta BD primero, luego Excel como fallback
READ_FROM_EXCEL = True
USE_HYBRID_MODE = True  # Nuevo: modo híbrido BD + Excel

# Importar DAL de portafolio para modo híbrido
try:
    from app.dal.portafolio_dal import (
        obtener_recaudo_campana_portafolio,
        obtener_recaudo_diario_portafolio,
        obtener_subcampanas_pais_portafolio,
        obtener_total_pais_portafolio,
        verificar_conexion_portafolio,
    )
    PORTAFOLIO_DISPONIBLE = True
except ImportError:
    PORTAFOLIO_DISPONIBLE = False

_EXCEL_CACHE = None

try:
    import pandas as pd
except Exception:
    pd = None


def _load_mapping():
    """Load optional mapping file `recaudo_mapping.json` from DATA folder.
    Returns a dict with optional keys: 'columns' (dict), 'inversionistas_by_pais' (dict), 'pais_aliases' (dict).
    """
    try:
        data_dir = _data_dir()
    except Exception:
        return {}

    mapping_file = os.path.join(data_dir, "recaudo_mapping.json")
    if not os.path.exists(mapping_file):
        return {}

    try:
        with open(mapping_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def obtener_recaudo_por_pais(id_pais: int, mes: int, anio: int):
    """
    Obtiene el recaudo total de un país (campaña grande) en un mes específico.
    Usa r.id_pais del recaudo y filtra por pais con nombre like %NPL% o similar.
    """
    # If Excel mode enabled, read from Excel files instead of DB
    if READ_FROM_EXCEL:
        return _obtener_recaudo_por_pais_excel(id_pais, mes, anio)

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            ISNULL(SUM(r.valor_recaudo), 0) as total,
            COUNT(r.id_recaudo) as cantidad
        FROM [marcacion] m
        INNER JOIN [marcacion_titular] mt ON m.telefono_marcado = mt.telefono_marcado
        INNER JOIN [recaudo] r ON mt.id_titular = r.id_titular
        INNER JOIN [pais] p ON r.id_pais = p.id_pais
        WHERE r.id_pais = ?
        AND MONTH(r.fecha_recaudo) = ?
        AND YEAR(r.fecha_recaudo) = ?
    """

    cursor.execute(query, (id_pais, mes, anio))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        "total": float(row[0]) if row and row[0] else 0.0,
        "cantidad": int(row[1]) if row and row[1] else 0,
    }


def _data_dir():
    # Use top-level BE/DATA exclusively (user confirmed that's the single source).
    repo_root = os.path.dirname(os.path.dirname(__file__))
    be_root = os.path.dirname(repo_root)
    data_dir = os.path.join(be_root, "DATA")
    return data_dir


def _load_all_data():
    """Load and cache all Excel/CSV files from app/DATA into a single DataFrame.
    Normalizes column names to lowercase and maps common column variants.
    IMPORTANTE: Lee la hoja 'Final' que contiene todos los datos de NPL, ACC, Peru, Chile.
    """
    global _EXCEL_CACHE, pd
    if _EXCEL_CACHE is not None:
        return _EXCEL_CACHE

    if pd is None:
        raise RuntimeError(
            "pandas is required to read Excel files. Install it in the backend venv."
        )

    data_dir = _data_dir()
    patterns = ["*.xlsx", "*.xls", "*.csv"]
    frames = []
    for pat in patterns:
        for f in glob.glob(os.path.join(data_dir, pat)):
            try:
                if f.lower().endswith(".csv"):
                    df = pd.read_csv(f)
                    df.columns = [str(c).strip().lower() for c in df.columns]
                    frames.append(df)
                else:
                    # Para archivos Excel, intentar leer la hoja "Final" primero
                    xls = pd.ExcelFile(f)
                    if 'Final' in xls.sheet_names:
                        df = pd.read_excel(f, sheet_name='Final')
                        df.columns = [str(c).strip().lower() for c in df.columns]
                        frames.append(df)
                    else:
                        # Si no hay hoja Final, leer la primera hoja
                        df = pd.read_excel(f)
                        df.columns = [str(c).strip().lower() for c in df.columns]
                        frames.append(df)
            except Exception as e:
                import logging
                logging.warning(f"Error leyendo archivo {f}: {e}")
                continue
            except Exception:
                # skip unreadable files
                continue

    if not frames:
        _EXCEL_CACHE = pd.DataFrame()
        return _EXCEL_CACHE

    df_all = pd.concat(frames, ignore_index=True, sort=False)

    # Normalize some common column names
    def _norm_name(s: str):
        s2 = str(s).strip().lower()
        # normalize accents and special chars
        for a, b in [
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
            ("ñ", "n"),
        ]:
            s2 = s2.replace(a, b)
        # remove spaces and punctuation
        for ch in [" ", "_", "-", "\\u00A0"]:
            s2 = s2.replace(ch, "")
        return s2

    rename_map = {}
    for col in df_all.columns:
        c = _norm_name(col)
        # La hoja Final usa "Campaña" para el país (NPL, ACC, Peru, Chile)
        # e "INVERSIONISTA" para la subcampaña
        if c in ("pais", "nombrepais", "nombrepaisportafolio", "campana"):
            rename_map[col] = "pais"
        if c in ("inversionista", "inversionistas", "investor"):
            rename_map[col] = "inversionista"
        if c in ("valor", "valorrecaudo", "montorecaudo", "monto", "valorrecaudo"):
            rename_map[col] = "valor_recaudo"
        if c in ("fecha", "fecharecaudo", "date"):
            rename_map[col] = "fecha_recaudo"
        if c in (
            "nombrecampana",
            "subcampana",
            "nombre_subcampana",
        ):
            rename_map[col] = "nombre_campana"
        if (
            c in ("anomes", "añomes", "anomes", "anomes")
            or "anom" in c
            or "añomes" in c
        ):
            # keep original name for año_mes-like columns (we'll build fecha_recaudo)
            rename_map[col] = "año_mes"
        if c in ("diahabil", "diahabil"):
            rename_map[col] = "dia_habil"
    # If a user mapping file exists, merge its column map (case-insensitive)
    mapping = _load_mapping()
    if mapping and isinstance(mapping.get("columns"), dict):
        for src, target in mapping.get("columns", {}).items():
            # find actual column name matching src case-insensitively
            for col in df_all.columns:
                if str(col).strip().lower() == str(src).strip().lower():
                    rename_map[col] = target
                    break

    df_all = df_all.rename(columns=rename_map)

    # If the source provides 'año_mes' + 'dia_habil' columns, build a proper fecha_recaudo
    if "año_mes" in df_all.columns and "dia_habil" in df_all.columns:
        try:
            # Normalize año_mes values like '2025-09' or '2025/09'
            am = (
                df_all["año_mes"]
                .astype(str)
                .str.replace("/", "-", regex=False)
                .str.strip()
            )
            # Convert dia_habil to int first to remove decimals, then to string with zfill
            dias = df_all["dia_habil"].fillna(1).astype(int).astype(str).str.zfill(2)
            fecha_str = am + "-" + dias
            df_all["fecha_recaudo"] = pd.to_datetime(
                fecha_str, format="%Y-%m-%d", errors="coerce"
            )
        except Exception:
            df_all["fecha_recaudo"] = pd.to_datetime(df_all["año_mes"], errors="coerce")

    # Ensure types
    if "fecha_recaudo" in df_all.columns:
        df_all["fecha_recaudo"] = pd.to_datetime(
            df_all["fecha_recaudo"], errors="coerce"
        )
    if "valor_recaudo" in df_all.columns:
        df_all["valor_recaudo"] = pd.to_numeric(
            df_all["valor_recaudo"], errors="coerce"
        ).fillna(0)

    _EXCEL_CACHE = df_all
    return _EXCEL_CACHE


def _obtener_recaudo_por_pais_excel(id_pais: int, mes: int, anio: int):
    """Attempt to compute totals by reading Excel files. id_pais is used to match a 'pais' string.
    We expect that calling code maps id_pais to a name; if integer, we will treat it as string.
    """
    df = _load_all_data()
    if df.empty:
        return {"total": 0.0, "cantidad": 0}

    # Resolve pais filter using mapping (if provided) or the id_pais as string
    pais_filter = _resolve_pais_filter(id_pais)

    # Build mask: search in 'pais' column if it exists, otherwise search in 'campaña' or 'nombre_campana'
    mask = pd.Series([False] * len(df))

    if "pais" in df.columns:
        mask = mask | df["pais"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    if "campaña" in df.columns:
        mask = mask | df["campaña"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    if "nombre_campana" in df.columns:
        mask = mask | df["nombre_campana"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    # If no relevant column exists, return zero
    if not (mask.any()):
        return {"total": 0.0, "cantidad": 0}

    # For campaign-grande view (e.g., NPL card) we include ALL inversionistas
    # for that pais, so filter only by pais + month/year.
    if "fecha_recaudo" in df.columns:
        mask = (
            mask
            & (df["fecha_recaudo"].dt.month == int(mes))
            & (df["fecha_recaudo"].dt.year == int(anio))
        )

    df_f = df[mask]
    total = (
        float(df_f["valor_recaudo"].sum()) if "valor_recaudo" in df_f.columns else 0.0
    )
    cantidad = int(len(df_f))
    return {"total": total, "cantidad": cantidad}


def _get_inversionistas_for_pais(pais_filter: str):
    """Return expected inversionista list for some known campaign grandes.
    The mapping follows the specification provided by the user.
    """
    p = pais_filter.lower()
    # Allow overrides from mapping file
    mapping = _load_mapping()
    if mapping and isinstance(mapping.get("inversionistas_by_pais"), dict):
        for pattern, invs in mapping.get("inversionistas_by_pais", {}).items():
            try:
                if pattern.strip().lower() in p:
                    return [str(x).upper() for x in invs]
            except Exception:
                continue
    # NPL Colombia
    if "npl" in p and ("col" in p or "colombia" in p):
        return ["BANCOLOMBIA", "BANCOOMEVA", "IFC", "PA", "TUYA"]
    # ACC (SystemGroup Colombia -> ACC)
    if "acc" in p or "systemgroup" in p or ("col" in p and "acc" in p):
        return ["ADAMANTINE", "ACCION", "JCAP", "PRA"]
    # NPL Peru (or PER)
    if "per" in p or "peru" in p:
        # there are two mentions: IFC and PROPIA depending on Excel source; return both
        return ["IFC", "PROPIA"]
    # NPL Chile mapping for NPL PER (user said use IFC)
    if "chile" in p:
        return ["IFC"]

    return []


def _resolve_pais_filter(id_pais):
    """Resolve an id_pais (could be int or string) to a pais string used in DATA files.
    If a mapping `pais_aliases` exists in the mapping file, use it (match by string key).
    Otherwise return str(id_pais).
    """
    mapping = _load_mapping()
    if mapping and isinstance(mapping.get("pais_aliases"), dict):
        try:
            key = str(id_pais)
            # direct lookup
            if key in mapping["pais_aliases"]:
                return mapping["pais_aliases"][key]
            # case-insensitive lookup
            for k, v in mapping["pais_aliases"].items():
                if str(k).strip().lower() == key.strip().lower():
                    return v
        except Exception:
            pass
    return str(id_pais)


def _filter_df_by_pais_and_inversionista(
    df, pais_filter: str, mes: int = None, anio: int = None
):
    """Filter the loaded DataFrame by pais substring and optionally by month/year and known inversionistas.
    Returns the filtered DataFrame.
    """
    if df.empty:
        return df

    # Build mask: search in 'pais' column if it exists, otherwise search in 'campaña' or 'nombre_campana'
    mask = pd.Series([False] * len(df))

    if "pais" in df.columns:
        mask = mask | df["pais"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    if "campaña" in df.columns:
        mask = mask | df["campaña"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    if "nombre_campana" in df.columns:
        mask = mask | df["nombre_campana"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    # By default apply inversionista whitelist, but allow caller to skip by passing
    # a boolean flag here in the future. For backward-compatibility we'll still
    # look up the inversionistas and apply the filter only when explicitly requested
    # via an attribute on df (not ideal) — instead expose a dedicated helper below.

    inv_list = _get_inversionistas_for_pais(str(pais_filter))
    if inv_list and "inversionista" in df.columns:
        # build mask for inversionistas (substring match any)
        inv_mask = (
            df["inversionista"]
            .astype(str)
            .str.upper()
            .apply(lambda s: any(inv in s for inv in inv_list))
        )
        mask = mask & inv_mask

    if mes is not None and anio is not None and "fecha_recaudo" in df.columns:
        mask = (
            mask
            & (df["fecha_recaudo"].dt.month == int(mes))
            & (df["fecha_recaudo"].dt.year == int(anio))
        )

    return df[mask]


def _filter_df_by_pais_only(df, pais_filter: str, mes: int = None, anio: int = None):
    """Filter by pais (substring) and optionally month/year, but do NOT apply inversionista whitelist."""
    if df.empty:
        return df

    # Build mask: search in 'pais' column if it exists, otherwise search in 'campaña' or 'nombre_campana'
    mask = pd.Series([False] * len(df))

    if "pais" in df.columns:
        mask = mask | df["pais"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    if "campaña" in df.columns:
        mask = mask | df["campaña"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    if "nombre_campana" in df.columns:
        mask = mask | df["nombre_campana"].astype(str).str.contains(
            str(pais_filter), case=False, na=False
        )

    if mes is not None and anio is not None and "fecha_recaudo" in df.columns:
        mask = (
            mask
            & (df["fecha_recaudo"].dt.month == int(mes))
            & (df["fecha_recaudo"].dt.year == int(anio))
        )

    return df[mask]


def _obtener_campanas_de_pais_excel(id_pais: int):
    df = _load_all_data()
    if df.empty:
        return []

    pais_filter = _resolve_pais_filter(id_pais)  # Use resolver to map aliases
    df_f = _filter_df_by_pais_only(df, pais_filter)

    # If no data found, return empty
    if df_f.empty:
        return []

    # For Peru and Chile, use inversionista column as subcampanas
    # Check if this is Peru or Chile by looking at the actual data
    if "nombre_campana" in df_f.columns:
        sample_campana = (
            df_f["nombre_campana"].dropna().iloc[0]
            if len(df_f["nombre_campana"].dropna()) > 0
            else None
        )
        # If nombre_campana is "Peru" or "Chile" (not subcampaña names), use inversionista instead
        if sample_campana and str(sample_campana).lower() in ["peru", "chile"]:
            if "inversionista" in df_f.columns:
                invs = df_f["inversionista"].dropna().astype(str).unique().tolist()
                return sorted([c.strip() for c in invs if c.strip()])

    # For other countries (COL, ACC), prefer explicit subcampana column when available
    if "nombre_campana" in df_f.columns:
        campanas = df_f["nombre_campana"].dropna().astype(str).unique().tolist()
        # Filter out country names (Peru, Chile) if they appear
        campanas = [
            c.strip()
            for c in campanas
            if c.strip() and c.strip().lower() not in ["peru", "chile", "colombia"]
        ]
        if campanas:
            return sorted(campanas)

    # Final fallback: if no subcampana column, use inversionista values as proxy
    if "inversionista" in df_f.columns:
        invs = df_f["inversionista"].dropna().astype(str).unique().tolist()
        invs = sorted([c.strip() for c in invs if c.strip()])
        return invs

    return []


def _obtener_recaudo_por_campana_pequena_excel(
    nombre_campana: str, mes: int, anio: int, id_pais: str = None
):
    """
    Busca el recaudo de una campaña pequeña (inversionista) en el Excel.
    
    La hoja Final tiene:
    - pais: NPL, ACC, Peru, Chile
    - inversionista: BANCOOMEVA, CREDIVALORES, IFC, etc.
    - año_mes: 2025-12, etc.
    - valor_recaudo: monto
    
    Primero filtra por país, luego por inversionista y mes/año.
    """
    df = _load_all_data()
    if df.empty:
        return {"nombre_campana": nombre_campana, "total": 0.0, "cantidad": 0}

    # Resolver el nombre del país para filtrar
    pais_excel = _mapear_pais_a_excel(id_pais) if id_pais else None
    
    # Empezar con todo el dataframe
    df_filtrado = df.copy()
    
    # 1. Filtrar por país si se especificó
    if pais_excel and "pais" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado["pais"].astype(str).str.upper() == pais_excel.upper()
        ]
    
    if df_filtrado.empty:
        return {"nombre_campana": nombre_campana, "total": 0.0, "cantidad": 0}
    
    # 2. Filtrar por inversionista (nombre_campana)
    if "inversionista" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado["inversionista"].astype(str).str.upper() == nombre_campana.upper()
        ]
    
    if df_filtrado.empty:
        return {"nombre_campana": nombre_campana, "total": 0.0, "cantidad": 0}
    
    # 3. Filtrar por mes/año
    if "año_mes" in df_filtrado.columns:
        # año_mes tiene formato "2025-12"
        mes_str = f"{anio}-{mes:02d}"
        df_filtrado = df_filtrado[
            df_filtrado["año_mes"].astype(str).str.strip() == mes_str
        ]
    elif "fecha_recaudo" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado["fecha_recaudo"].dt.month == int(mes)) &
            (df_filtrado["fecha_recaudo"].dt.year == int(anio))
        ]
    
    if df_filtrado.empty:
        return {"nombre_campana": nombre_campana, "total": 0.0, "cantidad": 0}
    
    # 4. Sumar valores
    total = float(df_filtrado["valor_recaudo"].sum()) if "valor_recaudo" in df_filtrado.columns else 0.0
    cantidad = len(df_filtrado)
    
    return {
        "nombre_campana": nombre_campana,
        "total": total,
        "cantidad": cantidad
    }


def obtener_total_excel_hasta_dia_habil(pais: str, inversionista: str, mes: int, anio: int, hasta_dia_habil: int) -> Dict:
    """
    Obtiene el total acumulado desde Excel para una inversión/subcampaña
    hasta el día hábil `hasta_dia_habil` (INCLUYE ese día hábil).

    Filtra por país (mapeado a Excel), por inversionista (nombre_subcampana/inversionista),
    y por mes/año. Si el archivo Excel contiene la columna `dia_habil`, se filtra
    directamente por `dia_habil <= hasta_dia_habil`. Si no, se calcula la fecha
    de corte usando `obtener_dias_habiles_mes` y se filtra por `fecha_recaudo <= fecha_corte`.

    Retorna dict: {"total": float, "cantidad": int}
    """
    df = _load_all_data()
    if df is None or df.empty:
        return {"total": 0.0, "cantidad": 0}

    pais_excel = _mapear_pais_a_excel(pais)
    # Build base mask by pais-like columns
    mask = pd.Series([False] * len(df))
    if "pais" in df.columns:
        mask = mask | df["pais"].astype(str).str.contains(str(pais_excel), case=False, na=False)
    if "campaña" in df.columns:
        mask = mask | df["campaña"].astype(str).str.contains(str(pais_excel), case=False, na=False)
    if "nombre_campana" in df.columns:
        mask = mask | df["nombre_campana"].astype(str).str.contains(str(pais_excel), case=False, na=False)

    df_f = df[mask]
    if df_f.empty:
        return {"total": 0.0, "cantidad": 0}

    # Filter by mes/anio
    if "año_mes" in df_f.columns:
        mes_str = f"{anio}-{mes:02d}"
        df_f = df_f[df_f["año_mes"].astype(str).str.strip() == mes_str]
    elif "fecha_recaudo" in df_f.columns:
        df_f = df_f[(df_f["fecha_recaudo"].dt.month == int(mes)) & (df_f["fecha_recaudo"].dt.year == int(anio))]

    if df_f.empty:
        return {"total": 0.0, "cantidad": 0}

    # Filter by inversionista (subcampaña)
    if inversionista and "inversionista" in df_f.columns:
        df_f = df_f[df_f["inversionista"].astype(str).str.upper().str.contains(str(inversionista).upper())]

    if df_f.empty:
        return {"total": 0.0, "cantidad": 0}

    # Apply dia_habil cutoff
    if "dia_habil" in df_f.columns:
        try:
            df_cut = df_f[df_f["dia_habil"].fillna(0).astype(int) <= int(hasta_dia_habil)]
        except Exception:
            df_cut = df_f
    else:
        # compute fecha corte from dias hábiles
        try:
            dias = obtener_dias_habiles_mes(anio, mes)
            if not dias or int(hasta_dia_habil) < 1 or int(hasta_dia_habil) > len(dias):
                # If out of bounds, use all month
                df_cut = df_f
            else:
                fecha_corte = dias[int(hasta_dia_habil) - 1]["fecha"]
                # fecha in dias is ISO string, convert to datetime
                df_cut = df_f[df_f.get("fecha_recaudo").notna() & (df_f["fecha_recaudo"] <= pd.to_datetime(fecha_corte))]
        except Exception:
            df_cut = df_f

    if df_cut.empty:
        return {"total": 0.0, "cantidad": 0}

    total = float(df_cut["valor_recaudo"].sum()) if "valor_recaudo" in df_cut.columns else 0.0
    cantidad = int(len(df_cut))
    return {"total": total, "cantidad": cantidad}


def _mapear_pais_a_excel(id_pais: str) -> str:
    """
    Mapea el nombre del país del FE al nombre en el Excel.
    FE -> Excel:
    - NPL COL, NPL -> NPL
    - ACC -> ACC
    - NPL PER, PERU -> Peru
    - NPL CHILE, CHILE -> Chile
    """
    if not id_pais:
        return None
    
    pais = str(id_pais).upper().strip()
    
    # Mapeo directo
    if pais in ("NPL", "NPL COL", "NPL COLOMBIA"):
        return "NPL"
    if pais in ("ACC", "ACC COL"):
        return "ACC"
    if pais in ("NPL PER", "NPL PERU", "PERU"):
        return "Peru"
    if pais in ("NPL CHILE", "CHILE"):
        return "Chile"
    
    # Si ya es el nombre exacto del Excel
    if pais in ("NPL", "ACC", "PERU", "CHILE"):
        return pais
    
    return pais


def obtener_campanas_de_pais(id_pais: int):
    """
    Obtiene la lista de campañas pequeñas (subcampañas) de un país
    Filtra por r.id_pais del recaudo
    """
    # If Excel mode enabled, use the Excel implementation
    if READ_FROM_EXCEL:
        return _obtener_campanas_de_pais_excel(id_pais)

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT DISTINCT 
            mt.nombre_campana
        FROM [marcacion] m
        INNER JOIN [marcacion_titular] mt ON m.telefono_marcado = mt.telefono_marcado
        INNER JOIN [recaudo] r ON mt.id_titular = r.id_titular
        INNER JOIN [pais] p ON r.id_pais = p.id_pais
        WHERE r.id_pais = ?
        AND mt.nombre_campana IS NOT NULL
        ORDER BY mt.nombre_campana
    """

    cursor.execute(query, (id_pais,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [row[0] for row in rows]


def obtener_recaudo_por_campana_pequena(
    nombre_campana: str, mes: int, anio: int, id_pais: str = None
):
    """
    Obtiene el recaudo de una subcampaña específica en un mes.
    
    MODO HÍBRIDO:
    1. Si hay datos en BD (vw_recaudos_portafolio), los usa
    2. Si no hay datos en BD, usa Excel como fallback
    """
    # ===================== MODO HÍBRIDO =====================
    if USE_HYBRID_MODE and PORTAFOLIO_DISPONIBLE and id_pais:
        # Verificar si esta campaña tiene datos en BD
        bd_name = get_campana_bd_name(str(id_pais), nombre_campana)
        
        if bd_name:
            # Intentar obtener de BD
            try:
                result = obtener_recaudo_campana_portafolio(bd_name, mes, anio)
                if result["total"] > 0 or result["cantidad"] > 0:
                    return {
                        "nombre_campana": nombre_campana,
                        "total": result["total"],
                        "cantidad": result["cantidad"],
                        "fuente": "BD"
                    }
            except Exception as e:
                import logging
                logging.warning(f"Error obteniendo de BD, usando Excel: {e}")
        
        # Si no hay datos en BD o hubo error, usar Excel
    
    # ===================== MODO EXCEL =====================
    # If Excel mode enabled, use the Excel implementation
    if READ_FROM_EXCEL:
        return _obtener_recaudo_por_campana_pequena_excel(
            nombre_campana, mes, anio, id_pais
        )

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            ISNULL(SUM(r.valor_recaudo), 0) as total,
            COUNT(r.id_recaudo) as cantidad
        FROM [marcacion] m
        INNER JOIN [marcacion_titular] mt ON m.telefono_marcado = mt.telefono_marcado
        INNER JOIN [recaudo] r ON mt.id_titular = r.id_titular
        INNER JOIN [pais] p ON r.id_pais = p.id_pais
        WHERE mt.nombre_campana = ?
        AND MONTH(r.fecha_recaudo) = ?
        AND YEAR(r.fecha_recaudo) = ?
    """

    cursor.execute(query, (nombre_campana, mes, anio))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        "nombre_campana": nombre_campana,
        "total": float(row[0]) if row and row[0] else 0.0,
        "cantidad": int(row[1]) if row and row[1] else 0,
    }


def obtener_recaudos_por_pais_con_subcampanas(id_pais: int, mes: int, anio: int):
    """
    Obtiene el recaudo total del país y el desglose por subcampañas.
    
    LÓGICA DE PRIORIDAD:
    1. BD tiene prioridad - si hay datos en BD, se usan
    2. Excel es fallback - si BD no tiene datos, se busca en Excel
    3. Si ninguno tiene datos, se muestra 0 (NO se oculta la campaña)
    
    PAÍSES:
    - NPL COL y ACC: Tienen algunas campañas en BD, otras en Excel
    - NPL PER y NPL CHILE: Solo Excel (no hay datos en BD)
    """
    pais_str = str(id_pais)
    
    # ===================== MODO HÍBRIDO =====================
    if USE_HYBRID_MODE and PORTAFOLIO_DISPONIBLE:
        try:
            # Verificar si este país tiene datos en BD
            subcampanas_bd_info = obtener_subcampanas_pais_portafolio(pais_str, mes, anio)
            
            # Si retorna None, el país no tiene datos en BD -> usar solo Excel
            if subcampanas_bd_info is None:
                # Usar modo Excel puro para este país
                return _obtener_recaudos_pais_excel_puro(id_pais, mes, anio)
            
            # Si retorna lista, procesar con lógica híbrida
            subcampanas_recaudo = []
            total_pais = 0.0
            cantidad_pais = 0
            
            # Obtener mapeo de nombres a IDs de inversionistas
            from app.database import get_connection1
            conn_inv = get_connection1()
            cursor_inv = conn_inv.cursor()
            cursor_inv.execute("""
                SELECT IDInversionistaQA, NombreInversionistaQA 
                FROM InversionistaQA 
                WHERE EsActivo = 1
            """)
            nombre_a_id = {row.NombreInversionistaQA.upper(): row.IDInversionistaQA for row in cursor_inv.fetchall()}
            cursor_inv.close()
            conn_inv.close()
            
            for sub in subcampanas_bd_info:
                nombre_campana = sub["nombre_campana"]
                total_campana = 0.0
                cantidad_campana = 0
                fuente = "SIN_DATOS"
                
                # PASO 1: Intentar BD primero
                if sub.get("tiene_datos_bd") and sub.get("total_bd", 0) > 0:
                    total_campana = sub["total_bd"]
                    cantidad_campana = sub["cantidad_bd"]
                    fuente = "BD"
                
                # PASO 2: Si BD no tiene datos, buscar en Excel
                if total_campana == 0:
                    recaudo_excel = _obtener_recaudo_por_campana_pequena_excel(
                        nombre_campana, mes, anio, pais_str
                    )
                    if recaudo_excel["total"] > 0:
                        total_campana = recaudo_excel["total"]
                        cantidad_campana = recaudo_excel["cantidad"]
                        fuente = "EXCEL"
                
                # PASO 3: Si no hay datos en BD ni Excel Y es INTERASEO, usar recaudo_manual
                if total_campana == 0 and nombre_campana.upper() == "INTERASEO":
                    try:
                        from app.database import get_connection1
                        # Mapear id_pais a nombre usado en tabla metas
                        nombre_pais_metas = "ACC" if pais_str == "2" else pais_str
                        
                        conn = get_connection1()
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT recaudo_manual 
                            FROM metas_campana_pequena 
                            WHERE nombre_pais = ? 
                            AND nombre_campana_pequena = ? 
                            AND mes = ? 
                            AND anio = ?
                        """, (nombre_pais_metas, nombre_campana, mes, anio))
                        row = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        
                        if row and row[0]:
                            total_campana = float(row[0])
                            fuente = "MANUAL"
                    except Exception as e:
                        pass  # Si falla, dejar en 0
                
                # PASO 4: SIEMPRE agregar la campaña (aunque tenga 0)
                # Buscar ID del inversionista por nombre
                id_inversionista = nombre_a_id.get(nombre_campana.upper())
                
                subcampanas_recaudo.append({
                    "nombre_campana": nombre_campana,
                    "total": total_campana,
                    "cantidad": cantidad_campana,
                    "fuente": fuente,
                    "id_inversionista": id_inversionista
                })
                total_pais += total_campana
                cantidad_pais += cantidad_campana
            
            return {
                "id_pais": id_pais,
                "mes": mes,
                "anio": anio,
                "total": total_pais,  # Para compatibilidad
                "total_pais": total_pais,
                "cantidad": cantidad_pais,  # Para compatibilidad
                "cantidad_pais": cantidad_pais,
                "subcampanas": subcampanas_recaudo,
                "modo": "HIBRIDO"
            }
            
        except Exception as e:
            import logging
            logging.warning(f"Error en modo híbrido, usando modo Excel: {e}")
    
    # ===================== MODO EXCEL PURO (FALLBACK) =====================
    return _obtener_recaudos_pais_excel_puro(id_pais, mes, anio)


def _obtener_recaudos_pais_excel_puro(id_pais: int, mes: int, anio: int):
    """
    Obtiene recaudos de un país usando SOLO Excel.
    Usado para países sin datos en BD (NPL PER, NPL CHILE) o como fallback.
    """
    pais_str = str(id_pais)
    campanas = obtener_campanas_de_pais(id_pais)

    subcampanas_recaudo = []
    total_calculado = 0.0
    cantidad_total = 0
    
    # Obtener mapeo de nombres a IDs de inversionistas
    from app.database import get_connection1
    conn_inv = get_connection1()
    cursor_inv = conn_inv.cursor()
    cursor_inv.execute("""
        SELECT IDInversionistaQA, NombreInversionistaQA 
        FROM InversionistaQA 
        WHERE EsActivo = 1
    """)
    nombre_a_id = {row.NombreInversionistaQA.upper(): row.IDInversionistaQA for row in cursor_inv.fetchall()}
    cursor_inv.close()
    conn_inv.close()
    
    for campana in campanas:
        recaudo = _obtener_recaudo_por_campana_pequena_excel(campana, mes, anio, pais_str)
        total_campana = recaudo["total"]
        cantidad_campana = recaudo["cantidad"]
        fuente = "EXCEL" if total_campana > 0 else "SIN_DATOS"
        
        # Si no hay datos en Excel Y es INTERASEO, buscar recaudo_manual
        if total_campana == 0 and campana.upper() == "INTERASEO":
            try:
                from app.database import get_connection1
                # Mapear id_pais a nombre usado en tabla metas
                nombre_pais_metas = "ACC" if pais_str == "2" else pais_str
                
                conn = get_connection1()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT recaudo_manual 
                    FROM metas_campana_pequena 
                    WHERE nombre_pais = ? 
                    AND nombre_campana_pequena = ? 
                    AND mes = ? 
                    AND anio = ?
                """, (nombre_pais_metas, campana, mes, anio))
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if row and row[0]:
                    total_campana = float(row[0])
                    fuente = "MANUAL"
            except Exception as e:
                pass  # Si falla, dejar en 0
        
        # Buscar ID del inversionista por nombre
        id_inversionista = nombre_a_id.get(campana.upper())
        
        subcampanas_recaudo.append({
            "nombre_campana": campana,
            "total": total_campana,
            "cantidad": cantidad_campana,
            "fuente": fuente,
            "id_inversionista": id_inversionista
        })
        
        total_calculado += total_campana
        cantidad_total += cantidad_campana

    return {
        "id_pais": id_pais,
        "mes": mes,
        "anio": anio,
        "total_pais": total_calculado,
        "cantidad_pais": cantidad_total,
        "subcampanas": subcampanas_recaudo,
        "modo": "EXCEL"
    }


def obtener_recaudo_diario_pais(id_pais: int, mes: int, anio: int):
    """
    Obtiene el recaudo agrupado por día para un país en un mes
    """
    # If Excel mode enabled, use Excel implementation
    if READ_FROM_EXCEL:
        return _obtener_recaudo_diario_pais_excel(id_pais, mes, anio)

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            CAST(r.fecha_recaudo AS DATE) as fecha,
            SUM(r.valor_recaudo) as total_dia,
            COUNT(r.id_recaudo) as cantidad_dia
        FROM [marcacion] m
        INNER JOIN [marcacion_titular] mt ON m.telefono_marcado = mt.telefono_marcado
        INNER JOIN [recaudo] r ON mt.id_titular = r.id_titular
        INNER JOIN [pais] p ON r.id_pais = p.id_pais
        WHERE r.id_pais = ?
        AND MONTH(r.fecha_recaudo) = ?
        AND YEAR(r.fecha_recaudo) = ?
        GROUP BY CAST(r.fecha_recaudo AS DATE)
        ORDER BY fecha
    """

    cursor.execute(query, (id_pais, mes, anio))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    resultado = []
    for row in rows:
        resultado.append(
            {
                "fecha": row[0].isoformat() if row[0] else None,
                "total": float(row[1]) if row[1] else 0.0,
                "cantidad": int(row[2]) if row[2] else 0,
            }
        )

    return resultado


def _obtener_recaudo_diario_pais_excel(id_pais: int, mes: int, anio: int):
    df = _load_all_data()
    if df.empty or "fecha_recaudo" not in df.columns:
        return []

    # Resolve pais filter from id_pais or name
    pais_filter = _resolve_pais_filter(id_pais)
    df_f = _filter_df_by_pais_only(df, pais_filter, mes, anio)
    if df_f.empty:
        return []

    # Group by date
    grouped = df_f.groupby(df_f["fecha_recaudo"].dt.date).agg({"valor_recaudo": "sum"})
    resultado = []
    for fecha, row in grouped.iterrows():
        resultado.append(
            {
                "fecha": fecha.isoformat(),
                "total": (
                    float(row["valor_recaudo"])
                    if row["valor_recaudo"] is not None
                    else 0.0
                ),
                "cantidad": int(df_f[df_f["fecha_recaudo"].dt.date == fecha].shape[0]),
            }
        )
    # sort by fecha
    resultado = sorted(resultado, key=lambda x: x["fecha"])
    return resultado


def obtener_recaudo_filtrado(
    nombre_campana: str, mes: int, anio: int, hasta_hoy: bool = False
):
    """
    Obtiene el recaudo total de una campaña en un mes específico usando el nombre de la campaña.
    Si hasta_hoy=True, solo suma recaudos hasta el día actual.
    """
    # If Excel mode enabled, use Excel implementation
    if READ_FROM_EXCEL:
        return _obtener_recaudo_filtrado_excel(nombre_campana, mes, anio, hasta_hoy)

    conn = get_connection()
    cursor = conn.cursor()

    # Base query
    query = """
        SELECT 
            ISNULL(SUM(r.valor_recaudo), 0) as total,
            COUNT(r.id_recaudo) as cantidad
        FROM [marcacion] m
        INNER JOIN [marcacion_titular] mt ON m.telefono_marcado = mt.telefono_marcado
        INNER JOIN [recaudo] r ON mt.id_titular = r.id_titular
        INNER JOIN [pais] p ON r.id_pais = p.id_pais
        WHERE mt.nombre_campana LIKE '%' + ? + '%'
        AND MONTH(r.fecha_recaudo) = ?
        AND YEAR(r.fecha_recaudo) = ?
    """

    # Si es "hasta hoy", agregar filtro de fecha
    if hasta_hoy:
        query += " AND CAST(r.fecha_recaudo AS DATE) <= CAST(GETDATE() AS DATE)"

    cursor.execute(query, (nombre_campana, mes, anio))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        "cantidad": int(row[1]) if row and row[1] else 0,
        "total": float(row[0]) if row and row[0] else 0.0,
    }


def _obtener_recaudo_filtrado_excel(
    nombre_campana: str, mes: int, anio: int, hasta_hoy: bool = False
):
    df = _load_all_data()
    if df.empty:
        return {"cantidad": 0, "total": 0.0}

    # Search in 'nombre_campana' OR 'inversionista'
    mask = pd.Series([False] * len(df))

    if "nombre_campana" in df.columns:
        mask = mask | df["nombre_campana"].astype(str).str.contains(
            str(nombre_campana), case=False, na=False
        )

    if "inversionista" in df.columns:
        mask = mask | df["inversionista"].astype(str).str.contains(
            str(nombre_campana), case=False, na=False
        )

    if "fecha_recaudo" in df.columns:
        mask = (
            mask
            & (df["fecha_recaudo"].dt.month == int(mes))
            & (df["fecha_recaudo"].dt.year == int(anio))
        )
        if hasta_hoy:
            hoy = pd.Timestamp.now().normalize()
            mask = mask & (df["fecha_recaudo"].dt.date <= hoy.date())

    df_f = df[mask]
    total = (
        float(df_f["valor_recaudo"].sum()) if "valor_recaudo" in df_f.columns else 0.0
    )
    cantidad = int(len(df_f))
    return {"cantidad": cantidad, "total": total}


def obtener_todos_los_recaudos():
    # 1️⃣ Conexión a la base de datos
    conn = get_connection()
    cursor = conn.cursor()

    # 2️⃣ Consulta SQL
    cursor.execute("SELECT * FROM recaudo")

    # 3️⃣ Obtener resultados
    rows = cursor.fetchall()

    # 4️⃣ Convertir los datos en diccionarios
    recaudos = []
    for row in rows:
        recaudos.append(
            {
                "id_recaudo": row.id_recaudo,
                "id_titular": row.id_titular,
                "fecha_recaudo": row.fecha_recaudo,
                "fecha_aplicacion": row.fecha_aplicacion,
                "valor_recaudo": row.valor_recaudo,
                "numero_obligacion": row.numero_obligacion,
                "id_tipo_pago": row.id_tipo_pago,
                "id_propietario": row.id_propietario,
                "id_banco": row.id_banco,
                "cuenta_origen_pago": row.cuenta_origen_pago,
                "codigo_cuenta": row.codigo_cuenta,
                "tipo_origen_pago": row.tipo_origen_pago,
                "id_sucursal": row.id_sucursal,
                "id_originador": row.id_originador,
                "id_vehiculo": row.id_vehiculo,
                "fecha_insert": row.fecha_insert,
                "observacion": row.observacion,
                "id_recaudo_teseo": row.id_recaudo_teseo,
                "id_estado_recaudo": row.id_estado_recaudo,
                "fecha_modificacion": row.fecha_modificacion,
                "id_pais": row.id_pais,
            }
        )

    # 5️⃣ Cerrar conexión
    cursor.close()
    conn.close()

    # 6️⃣ Retornar los datos al BLL
    return recaudos
