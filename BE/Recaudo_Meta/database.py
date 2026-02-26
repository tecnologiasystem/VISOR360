"""
Configuración de conexión a SQL Server vía pyodbc
Con pooling, manejo de errores y timeouts
"""
import pyodbc
from contextlib import contextmanager
from typing import Generator, Optional, List, Dict, Any
import logging
from config import get_settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


class DatabaseError(Exception):
    """Excepción personalizada para errores de base de datos"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class DatabaseConnection:
    """Clase para manejar conexiones a SQL Server con pooling"""
    
    _pool: List[pyodbc.Connection] = []
    _pool_size: int = settings.DB_POOL_SIZE
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Genera el string de conexión"""
        return (
            f"DRIVER={{{settings.DB_DRIVER}}};"
            f"SERVER={settings.DB_SERVER};"
            f"DATABASE={settings.DB_DATABASE};"
            f"UID={settings.DB_USERNAME};"
            f"PWD={settings.DB_PASSWORD};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
            f"Connection Timeout={settings.DB_TIMEOUT};"
        )
    
    @classmethod
    def create_connection(cls) -> pyodbc.Connection:
        """Crea una nueva conexión"""
        try:
            conn = pyodbc.connect(
                cls.get_connection_string(),
                autocommit=False,
                timeout=settings.DB_TIMEOUT
            )
            logger.debug("Nueva conexión creada")
            return conn
        except pyodbc.Error as e:
            logger.error(f"Error al crear conexión: {e}")
            raise DatabaseError("No se pudo conectar a la base de datos", e)
    
    @classmethod
    def get_connection(cls) -> pyodbc.Connection:
        """Obtiene una conexión del pool o crea una nueva"""
        if cls._pool:
            conn = cls._pool.pop()
            try:
                # Verificar que la conexión siga activa
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return conn
            except pyodbc.Error:
                logger.warning("Conexión del pool inválida, creando nueva")
                return cls.create_connection()
        return cls.create_connection()
    
    @classmethod
    def return_connection(cls, conn: pyodbc.Connection):
        """Devuelve una conexión al pool"""
        if len(cls._pool) < cls._pool_size:
            try:
                conn.rollback()  # Limpiar transacciones pendientes
                cls._pool.append(conn)
                logger.debug("Conexión devuelta al pool")
            except pyodbc.Error:
                logger.warning("Error al devolver conexión, cerrando")
                cls.close_connection(conn)
        else:
            cls.close_connection(conn)
    
    @classmethod
    def close_connection(cls, conn: pyodbc.Connection):
        """Cierra una conexión de forma segura"""
        try:
            conn.close()
            logger.debug("Conexión cerrada")
        except pyodbc.Error as e:
            logger.warning(f"Error al cerrar conexión: {e}")


@contextmanager
def get_db_connection() -> Generator[pyodbc.Connection, None, None]:
    """
    Context manager para obtener una conexión de la BD.
    Uso:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            ...
    """
    conn = None
    try:
        conn = DatabaseConnection.get_connection()
        yield conn
        conn.commit()
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Error de base de datos: {e}")
        raise DatabaseError(f"Error en operación de base de datos: {str(e)}", e)
    finally:
        if conn:
            DatabaseConnection.return_connection(conn)


@contextmanager
def get_db_cursor() -> Generator[pyodbc.Cursor, None, None]:
    """
    Context manager para obtener un cursor directamente.
    Uso:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT ...")
            rows = cursor.fetchall()
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()


def execute_sp(
    sp_name: str,
    params: Optional[Dict[str, Any]] = None,
    fetch_results: bool = True
) -> Dict[str, Any]:
    """
    Ejecuta un stored procedure con parámetros nombrados.
    
    Args:
        sp_name: Nombre del stored procedure
        params: Diccionario de parámetros
        fetch_results: Si debe retornar resultados
    
    Returns:
        Dict con 'rows' (lista de diccionarios), 'rowcount' y 'output_params'
    """
    params = params or {}
    
    # Construir la llamada al SP con parámetros
    param_placeholders = ", ".join([f"@{k}=?" for k in params.keys()])
    sql = f"EXEC {sp_name} {param_placeholders}" if params else f"EXEC {sp_name}"
    
    logger.info(f"Ejecutando SP: {sp_name} con params: {list(params.keys())}")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, list(params.values()))
            
            result = {
                "rows": [],
                "rowcount": cursor.rowcount,
                "output_params": {}
            }
            
            if fetch_results:
                # Intentar obtener resultados
                try:
                    columns = [column[0] for column in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    result["rows"] = [dict(zip(columns, row)) for row in rows]
                except pyodbc.ProgrammingError:
                    # El SP no retornó resultados
                    pass
            
            conn.commit()
            logger.info(f"SP {sp_name} ejecutado exitosamente. Filas afectadas: {result['rowcount']}")
            return result
            
        except pyodbc.Error as e:
            conn.rollback()
            logger.error(f"Error ejecutando SP {sp_name}: {e}")
            raise DatabaseError(f"Error ejecutando {sp_name}: {str(e)}", e)
        finally:
            cursor.close()


def execute_query(
    sql: str,
    params: Optional[tuple] = None
) -> List[Dict[str, Any]]:
    """
    Ejecuta una consulta SQL y retorna los resultados como lista de diccionarios.
    
    Args:
        sql: Consulta SQL (usar ? para parámetros)
        params: Tupla de parámetros
    
    Returns:
        Lista de diccionarios con los resultados
    """
    with get_db_cursor() as cursor:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        return []


def test_connection() -> bool:
    """Prueba la conexión a la base de datos"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1 AS test")
            result = cursor.fetchone()
            return result[0] == 1
    except Exception as e:
        logger.error(f"Error en test de conexión: {e}")
        return False
