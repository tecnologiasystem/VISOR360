"""
Modelos Pydantic comunes y respuestas genéricas
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime


class APIResponse(BaseModel):
    """Respuesta genérica de la API"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Respuesta de error"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Respuesta paginada"""
    success: bool = True
    data: List[Any]
    total: int
    page: int = 1
    page_size: int = 50
    total_pages: int = 1


class HealthCheckResponse(BaseModel):
    """Respuesta del health check"""
    status: str = "healthy"
    database: str = "connected"
    timestamp: datetime
    version: str


# Modelos para filtros de consulta
class FiltrosRecaudo(BaseModel):
    """Filtros para consultas de recaudo"""
    IDCampanasQA: Optional[int] = Field(None, description="Filtrar por campaña")
    IDInversionistaQA: Optional[int] = Field(None, description="Filtrar por inversionista")
    AnioMes: Optional[str] = Field(None, description="Periodo específico YYYY-MM")
    AnioMesDesde: Optional[str] = Field(None, description="Periodo desde YYYY-MM")
    AnioMesHasta: Optional[str] = Field(None, description="Periodo hasta YYYY-MM")
    SoloActivos: bool = Field(True, description="Solo registros activos")


class FiltrosDashboard(BaseModel):
    """Filtros específicos para dashboard"""
    campanas: Optional[List[int]] = Field(None, description="Lista de IDs de campañas")
    inversionistas: Optional[List[int]] = Field(None, description="Lista de IDs de inversionistas")
    periodo_inicio: Optional[str] = Field(None, description="Inicio del rango")
    periodo_fin: Optional[str] = Field(None, description="Fin del rango")
