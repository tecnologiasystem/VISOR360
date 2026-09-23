import os
from pathlib import Path
import pyodbc
# Las credenciales se leen de variables de entorno (archivo .env local, que NO se
# versiona). Ver BE/.env.example para la plantilla. Nunca poner secretos aqui.
# Se carga el .env de la raiz de BE aqui mismo para que funcione sin importar el
# orden de imports y sin depender de que main.py lo cargue antes.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:  # python-dotenv no instalado: se usan solo variables de entorno reales
    pass

# ----------------------------- BD 1 (export_planeacion) -----------------------------
DB1_CONFIG = {
    "server": os.getenv("DB1_SERVER", "172.18.79.20"),
    "database": os.getenv("DB1_DATABASE", "export_planeacion"),
    "username": os.getenv("DB1_USERNAME", ""),
    "password": os.getenv("DB1_PASSWORD", "")
}

def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB1_CONFIG['server']};"
        f"DATABASE={DB1_CONFIG['database']};"
        f"UID={DB1_CONFIG['username']};"
        f"PWD={DB1_CONFIG['password']}"
    )
    return pyodbc.connect(conn_str)

# ----------------------------- BD 2 (LOGS) -----------------------------
DB2_CONFIG = {
    "server": os.getenv("DB2_SERVER", "172.18.72.111"),
    "database": os.getenv("DB2_DATABASE", "LOGS"),
    "username": os.getenv("DB2_USERNAME", ""),
    "password": os.getenv("DB2_PASSWORD", "")
}

def get_connection1():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB2_CONFIG['server']};"
        f"DATABASE={DB2_CONFIG['database']};"
        f"UID={DB2_CONFIG['username']};"
        f"PWD={DB2_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )

    return pyodbc.connect(conn_str, autocommit=True)

# ----------------------------- BD 3 (Portafolio - vw_recaudos_portafolio) -----------------------------
# Esta BD contiene la vista vw_recaudos_portafolio con datos de Colombia
# NOTA: La vista está en la misma BD export_planeacion, usamos las mismas credenciales
# Campañas disponibles:
#   NPL: SYSTEMGROUP CREDIVALORES NPL
#   ACC: SYSTEMGROUP ACCION FIDUCIARIA- DENTIX, SYSTEMGROUP ADAMANTINE - COLPATRIA NPL,
#        SYSTEMGROUP JCAP, SYSTEMGROUP PRA GROUP
DB3_CONFIG = {
    "server": os.getenv("DB3_SERVER", "172.18.79.20"),  # Mismo servidor que BD1
    "database": os.getenv("DB3_DATABASE", "export_planeacion"),  # La vista está en esta BD
    "username": os.getenv("DB3_USERNAME", ""),
    "password": os.getenv("DB3_PASSWORD", "")
}

def get_connection_portafolio():
    """
    Conexión a la BD que contiene la vista vw_recaudos_portafolio.
    Usada para obtener datos de recaudo de campañas pequeñas de Colombia.
    NOTA: Usa la misma conexión que BD1 ya que la vista está en export_planeacion.
    """
    # Reutilizamos la conexión BD1 ya que la vista está en la misma BD
    return get_connection()


# ----------------------------- Lista de Campañas Pequeñas por País -----------------------------
# Este diccionario lista las subcampañas de cada país/campaña grande
CAMPANAS_PEQUENAS = {
    "NPL COL": ["BANCOOMEVA", "CREDIVALORES", "IFC", "PA", "TUYA"],
    "NPL": ["BANCOOMEVA", "CREDIVALORES", "IFC", "PA", "TUYA"],
    "ACC": ["Accion", "Adamantine", "interaseo", "jcap", "PRA"],
    "NPL PER": ["IFC", "PROPIA"],
    "NPL PERU": ["IFC", "PROPIA"],
    "NPL CHILE": ["IFC"],
}


# ----------------------------- Mapeo de Campañas Pequeñas a Nombres en BD -----------------------------
# Este mapeo relaciona las campañas pequeñas del FE con los nombres en la vista vw_recaudos_portafoliov2
CAMPANAS_PEQUENAS_BD_MAPPING = {
    # NPL Colombia - Todas las campañas ahora tienen datos en BD (vw_recaudos_portafoliov2)
    "NPL": {
        "BANCOOMEVA": "BANCOOMEVA",  # Tiene datos en BD
        "CREDIVALORES": "SYSTEMGROUP CREDIVALORES NPL",  # Tiene datos en BD
        "IFC": "IFC",  # Tiene datos en BD
        "PA": "PA",  # Tiene datos en BD
        "TUYA": "TUYA",  # Tiene datos en BD
    },
    "NPL COL": {
        "BANCOOMEVA": "BANCOOMEVA",  # Tiene datos en BD
        "CREDIVALORES": "SYSTEMGROUP CREDIVALORES NPL",  # Tiene datos en BD
        "IFC": "IFC",  # Tiene datos en BD
        "PA": "PA",  # Tiene datos en BD
        "TUYA": "TUYA",  # Tiene datos en BD
    },
    # ACC (Campañas especiales) - Todas excepto interaseo
    "ACC": {
        "ACCION": "SYSTEMGROUP ACCION FIDUCIARIA- DENTIX",
        "ADAMANTINE": "SYSTEMGROUP ADAMANTINE - COLPATRIA NPL",
        "CREDIVALORES": "SYSTEMGROUP CREDIVALORES NPL",  # Fix: Es NPL, no COL
        "INTERASEO": None,  # NO hay datos en BD, usará Excel
        "JCAP": "SYSTEMGROUP JCAP",
        "PRAGROUP": "SYSTEMGROUP PRA GROUP",
    },
    # ACC COL - Alias para ACC con mismo mapeo
    "ACC COL": {
        "ACCION": "SYSTEMGROUP ACCION FIDUCIARIA- DENTIX",
        "ADAMANTINE": "SYSTEMGROUP ADAMANTINE - COLPATRIA NPL",
        "CREDIVALORES": "SYSTEMGROUP CREDIVALORES NPL",  # Fix: Es NPL, no COL
        "INTERASEO": None,  # NO hay datos en BD, usará Excel
        "JCAP": "SYSTEMGROUP JCAP",
        "PRAGROUP": "SYSTEMGROUP PRA GROUP",
    },
    # Alias adicionales para compatibilidad
    "SYSTEMGROUP COLOMBIA": {
        "Accion": "SYSTEMGROUP ACCION FIDUCIARIA- DENTIX",
        "Adamantine": "SYSTEMGROUP ADAMANTINE - COLPATRIA NPL",
        "interaseo": None,
        "jcap": "SYSTEMGROUP JCAP",
        "PRA": "SYSTEMGROUP PRA GROUP",
    },
    # NPL Perú y Chile - NO están en BD, usan Excel
    "NPL PER": {
        "IFC": None,
        "PROPIA": None,  
    },    
    "NPL CHILE": {
        "IFC": "SYSTEMGROUP CHILE",  # Fix: Enable Chile data from BD
    },
}

def get_campana_bd_name(pais: str, campana_pequena: str) -> str:
    """
    Obtiene el nombre de la campaña en la BD dado el país y nombre de campaña pequeña del FE.
    Retorna None si no hay mapeo (debe usarse Excel).
    """
    pais_upper = pais.upper().strip()
    
    # Buscar en el mapeo
    for pais_key in CAMPANAS_PEQUENAS_BD_MAPPING:
        if pais_key.upper() in pais_upper or pais_upper in pais_key.upper():
            campanas = CAMPANAS_PEQUENAS_BD_MAPPING[pais_key]
            # Buscar la campaña (case insensitive)
            for camp_key, bd_name in campanas.items():
                if camp_key.lower() == campana_pequena.lower():
                    return bd_name
                # También buscar si el nombre de BD coincide
                if bd_name and campana_pequena.lower() in bd_name.lower():
                    return bd_name
    
    return None

def campana_tiene_datos_en_bd(pais: str, campana_pequena: str) -> bool:
    """
    Verifica si una campaña pequeña tiene datos en la BD.
    Retorna True si hay mapeo y el nombre BD no es None.
    """
    bd_name = get_campana_bd_name(pais, campana_pequena)
    return bd_name is not None


