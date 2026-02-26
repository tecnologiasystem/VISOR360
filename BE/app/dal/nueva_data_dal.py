# DAL para leer desde el archivo consolidado "Nueva Data.xlsx"
# Este archivo NO modifica el código existente, es completamente independiente

import pandas as pd
import os
from typing import Dict, List

_CACHE = None


def _normalize_campaign_name(nombre: str) -> str:
    """Normaliza nombres de campaña para aceptar múltiples variantes"""
    nombre = nombre.strip().upper()
    
    # Mapeo flexible para Perú
    if "PERU" in nombre or nombre == "NPL PER":
        return "NPL PER"
    
    # Mapeo flexible para Colombia
    if "COLOMBIA" in nombre or nombre == "NPL COL":
        return "NPL COL"
    
    # Mapeo flexible para Chile
    if "CHILE" in nombre:
        return "NPL CHILE"
    
    # ACC se mantiene igual
    if "ACC" in nombre:
        return "ACC"
    
    return nombre


def _clear_cache():
    """Clear the cache to force reload"""
    global _CACHE
    _CACHE = None


def _data_dir():
    """Get the DATA directory path"""
    repo_root = os.path.dirname(os.path.dirname(__file__))
    be_root = os.path.dirname(repo_root)
    return os.path.join(be_root, "DATA")


def _load_nueva_data():
    """Load and cache the Nueva Data.xlsx file"""
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    try:
        data_path = os.path.join(_data_dir(), "Nueva Data.xlsx")
        df = pd.read_excel(data_path, sheet_name="Final")

        # Normalize column names
        df.columns = [str(col).strip().upper() for col in df.columns]

        # Map campaign names to match UI expectations
        campaign_map = {
            "Peru": "NPL PER",
            "Chile": "NPL CHILE",
            "NPL": "NPL COL",
            "ACC": "ACC",
        }

        if "CAMPAÑA" in df.columns:
            df["CAMPAÑA"] = df["CAMPAÑA"].astype(str).str.strip()
            df["CAMPAÑA"] = df["CAMPAÑA"].replace(campaign_map)

        # Parse AÑO_MES to extract mes and anio
        if "AÑO_MES" in df.columns:
            df["AÑO_MES"] = df["AÑO_MES"].astype(str).str.strip()
            df[["ANIO", "MES"]] = df["AÑO_MES"].str.split("-", expand=True)
            df["MES"] = pd.to_numeric(df["MES"], errors="coerce").astype("Int64")
            df["ANIO"] = pd.to_numeric(df["ANIO"], errors="coerce").astype("Int64")

        # Clean numeric columns
        if "VALOR RECAUDO" in df.columns:
            df["VALOR_RECAUDO"] = pd.to_numeric(
                df["VALOR RECAUDO"], errors="coerce"
            ).fillna(0)

        if "META" in df.columns:
            df["META"] = pd.to_numeric(df["META"], errors="coerce").fillna(0)

        # Normalize inversionista to lowercase for consistency
        if "INVERSIONISTA" in df.columns:
            df["INVERSIONISTA"] = (
                df["INVERSIONISTA"].astype(str).str.strip().str.lower()
            )

        _CACHE = df
        return df
    except Exception as e:
        print(f"Error loading Nueva Data: {e}")
        return pd.DataFrame()


def obtener_recaudo_pais_nueva_data(nombre_pais: str, mes: int, anio: int) -> Dict:
    """
    Obtiene el recaudo de un país desde Nueva Data.xlsx
    Retorna estructura compatible con el formato esperado por el frontend
    """
    # Normalizar nombre del país usando la función centralizada
    nombre_normalizado = _normalize_campaign_name(nombre_pais)
    
    df = _load_nueva_data()
    if df.empty:
        return {
            "id_pais": nombre_normalizado,
            "mes": mes,
            "anio": anio,
            "total_pais": 0.0,
            "cantidad_pais": 0,
            "subcampanas": [],
        }

    # Filter by campaign, mes, anio
    mask = (df["CAMPAÑA"] == nombre_normalizado) & (df["MES"] == mes) & (df["ANIO"] == anio)
    df_filtered = df[mask]

    if df_filtered.empty:
        return {
            "id_pais": nombre_pais,
            "mes": mes,
            "anio": anio,
            "total_pais": 0.0,
            "cantidad_pais": 0,
            "subcampanas": [],
        }

    # Calculate total recaudo
    total_recaudo = float(df_filtered["VALOR_RECAUDO"].sum())

    # Group by inversionista (subcampaña)
    subcampanas = []
    if "INVERSIONISTA" in df_filtered.columns:
        grouped = df_filtered.groupby("INVERSIONISTA")["VALOR_RECAUDO"].sum()
        for inv, valor in grouped.items():
            subcampanas.append(
                {
                    "nombre_campana": str(inv).upper(),
                    "total": float(valor),
                    "cantidad": int(
                        len(df_filtered[df_filtered["INVERSIONISTA"] == inv])
                    ),
                }
            )

    return {
        "id_pais": nombre_pais,
        "mes": mes,
        "anio": anio,
        "total_pais": total_recaudo,
        "cantidad_pais": len(df_filtered),
        "subcampanas": sorted(subcampanas, key=lambda x: x["nombre_campana"]),
    }


def obtener_meta_pais_nueva_data(nombre_pais: str, mes: int, anio: int) -> Dict:
    """
    Obtiene las metas de un país desde Nueva Data.xlsx
    Retorna estructura compatible con el formato esperado por el frontend
    """
    # Normalizar nombre del país para aceptar variantes
    nombre_normalizado = nombre_pais.strip()
    if nombre_normalizado == "NPL PERU":
        nombre_normalizado = "NPL PER"
    elif nombre_normalizado == "NPL COLOMBIA":
        nombre_normalizado = "NPL COL"
    
    df = _load_nueva_data()
    if df.empty:
        return {
            "nombre_pais": nombre_normalizado,
            "mes": mes,
            "anio": anio,
            "meta_total": 0.0,
            "metas_subcampanas": [],
        }

    # Filter by campaign, mes, anio
    mask = (df["CAMPAÑA"] == nombre_normalizado) & (df["MES"] == mes) & (df["ANIO"] == anio)
    df_filtered = df[mask]

    if df_filtered.empty:
        return {
            "nombre_pais": nombre_pais,
            "mes": mes,
            "anio": anio,
            "meta_total": 0.0,
            "metas_subcampanas": [],
        }

    # Calculate total meta
    meta_total = float(df_filtered["META"].sum())

    # Group by inversionista (subcampaña)
    metas_subcampanas = []
    if "INVERSIONISTA" in df_filtered.columns:
        grouped = df_filtered.groupby("INVERSIONISTA")["META"].sum()
        for inv, valor in grouped.items():
            metas_subcampanas.append(
                {"nombre_campana": str(inv).upper(), "meta_valor": float(valor)}
            )

    return {
        "nombre_pais": nombre_normalizado,
        "mes": mes,
        "anio": anio,
        "meta_total": meta_total,
        "metas_subcampanas": sorted(
            metas_subcampanas, key=lambda x: x["nombre_campana"]
        ),
    }
