"""
Modelos Pydantic para Carga de Recaudo (desde Excel/Staging)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrigenCarga(str, Enum):
    """Origen de la carga de datos"""
    EXCEL = "EXCEL"
    APP = "APP"
    API = "API"


class CargaRecaudoBase(BaseModel):
    """Modelo base de Carga de Recaudo"""
    PeriodoAnioMes: Optional[str] = Field(None, max_length=7, description="Periodo YYYY-MM")
    NombreArchivo: Optional[str] = Field(None, max_length=255, description="Nombre del archivo")
    RutaArchivo: Optional[str] = Field(None, max_length=500, description="Ruta del archivo")
    Origen: OrigenCarga = Field(default=OrigenCarga.EXCEL, description="Origen de la carga")
    Observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones")


class CargaRecaudoCreate(CargaRecaudoBase):
    """Modelo para crear una carga"""
    IDUsuarioCarga: int = Field(..., description="ID del usuario que realiza la carga")


class CargaRecaudo(CargaRecaudoBase):
    """Modelo completo de Carga de Recaudo"""
    IDCargaRecaudoQA: int = Field(..., description="ID único de la carga")
    FechaCarga: datetime = Field(..., description="Fecha de la carga")
    IDUsuarioCarga: int = Field(..., description="ID del usuario que cargó")
    
    class Config:
        from_attributes = True


# Modelo para el staging (datos crudos del Excel)
class RecaudoStagingRow(BaseModel):
    """Fila de staging del Excel"""
    Campana: str = Field(..., max_length=50, description="Nombre de campaña del archivo")
    AnioMes: str = Field(..., max_length=7, description="Periodo YYYY-MM")
    DiaHabil: int = Field(..., ge=1, le=31, description="Día hábil")
    ValorRecaudo: Optional[str] = Field(None, max_length=50, description="Valor como string")
    Inversionista: str = Field(..., max_length=100, description="Nombre inversionista")
    Meta: Optional[str] = Field(None, max_length=50, description="Meta como string")


# Modelo de petición para iniciar carga desde staging
class CargaDesdeExcelRequest(BaseModel):
    """Petición para ejecutar carga desde staging"""
    NombreArchivo: str = Field(..., max_length=255, description="Nombre del archivo Excel")
    RutaArchivo: Optional[str] = Field(None, max_length=500, description="Ruta del archivo")
    IDUsuarioCarga: int = Field(..., description="ID del usuario que realiza la carga")
    Origen: OrigenCarga = Field(default=OrigenCarga.EXCEL, description="Origen de los datos")
    PeriodoAnioMes: Optional[str] = Field(None, max_length=7, description="Periodo específico (opcional)")


# Modelo de respuesta después de cargar
class CargaRecaudoResponse(BaseModel):
    """Respuesta después de ejecutar la carga"""
    success: bool = True
    IDCargaRecaudoQA: int = Field(..., description="ID de la carga creada")
    FilasAfectadas: int = Field(..., description="Número de filas procesadas")
    PeriodoAnioMes: Optional[str] = Field(None, description="Periodo procesado")
    message: str = Field(default="Carga procesada exitosamente")


class CargaRecaudoListResponse(BaseModel):
    """Respuesta para lista de cargas"""
    success: bool = True
    data: List[CargaRecaudo]
    total: int


# Modelo para auditoría
class AuditoriaRecaudo(BaseModel):
    """Modelo de auditoría de cambios"""
    IDAuditoriaRecaudoQA: int
    IDRecaudoQA: int
    IDCargaRecaudoQA: Optional[int]
    FechaEvento: datetime
    IDUsuarioEvento: int
    TipoOperacion: str = Field(..., max_length=1, description="I=Insert, U=Update, D=Delete")
    ValorRecaudo_Anterior: Optional[float]
    ValorRecaudo_Nuevo: Optional[float]
    Meta_Anterior: Optional[float]
    Meta_Nuevo: Optional[float]
    Origen: str = Field(default="APP", max_length=20)
    Observaciones: Optional[str]
    
    class Config:
        from_attributes = True
