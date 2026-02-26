"""
Configuración del microservicio Recaudo Meta
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Configuración del servidor
    APP_NAME: str = "Recaudo Meta API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8002  # Puerto diferente al main_nueva_data.py
    
    # Configuración de la base de datos LOGS
    DB_SERVER: str = "172.18.72.111"
    DB_DATABASE: str = "LOGS"
    DB_USERNAME: str = "NEXUM"
    DB_PASSWORD: str = "REDACTED_ROTATE_THIS_PASSWORD"
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_TIMEOUT: int = 30
    DB_POOL_SIZE: int = 5
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración cacheada"""
    return Settings()
