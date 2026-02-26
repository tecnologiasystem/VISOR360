"""
Modelos Pydantic para Recaudo Diario y Metas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import re


class RecaudoDiarioBase(BaseModel):
    """Modelo base de Recaudo Diario"""
    IDCampanasInversionistasQA: int = Field(..., description="ID de relación campaña-inversionista")
    AnioMes: str = Field(..., min_length=7, max_length=7, description="Periodo en formato YYYY-MM")
    DiaHabil: int = Field(..., ge=1, le=31, description="Día hábil del mes")
    ValorRecaudo: Optional[Decimal] = Field(None, description="Valor de recaudo")
    Meta: Optional[Decimal] = Field(None, description="Meta establecida")
    
    @field_validator('AnioMes')
    @classmethod
    def validate_anio_mes(cls, v: str) -> str:
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('AnioMes debe tener formato YYYY-MM')
        year, month = v.split('-')
        if not (1 <= int(month) <= 12):
            raise ValueError('Mes debe estar entre 01 y 12')
        return v


class RecaudoDiarioCreate(RecaudoDiarioBase):
    """Modelo para crear un registro de Recaudo Diario"""
    IDUsuarioCreacion: int = Field(..., description="ID del usuario que crea")
    IDCargaRecaudoQA: Optional[int] = Field(None, description="ID de la carga asociada")


class RecaudoDiarioUpdate(BaseModel):
    """Modelo para actualizar un registro de Recaudo Diario"""
    ValorRecaudo: Optional[Decimal] = Field(None, description="Nuevo valor de recaudo")
    Meta: Optional[Decimal] = Field(None, description="Nueva meta")
    IDUsuarioUltimaActualizacion: int = Field(..., description="ID del usuario que actualiza")


class RecaudoDiario(RecaudoDiarioBase):
    """Modelo completo de Recaudo Diario"""
    IDRecaudoQA: int = Field(..., description="ID único del registro")
    IDCargaRecaudoQA: Optional[int] = Field(None, description="ID de la carga asociada")
    FechaCreacion: datetime = Field(..., description="Fecha de creación")
    IDUsuarioCreacion: int = Field(..., description="ID del usuario que creó")
    FechaUltimaActualizacion: Optional[datetime] = Field(None, description="Última actualización")
    IDUsuarioUltimaActualizacion: Optional[int] = Field(None, description="Usuario que actualizó")
    EsActivo: bool = Field(True, description="Si está activo")
    
    class Config:
        from_attributes = True


class RecaudoDiarioExtendido(RecaudoDiario):
    """Modelo extendido con datos de campaña e inversionista"""
    NombreCampana: Optional[str] = None
    NombreInversionistaQA: Optional[str] = None
    IDCampanasQA: Optional[int] = None
    IDInversionistaQA: Optional[int] = None
    
    class Config:
        from_attributes = True


# Modelos para respuestas del dashboard
class ResumenRecaudoDia(BaseModel):
    """Resumen de recaudo por día para gráficos del FE"""
    IDCampanasQA: int
    NombreCampana: str
    IDInversionistaQA: int
    NombreInversionistaQA: str
    AnioMes: str
    DiaHabil: int
    ValorRecaudoDia: Decimal = Field(default=Decimal('0'))
    MetaDia: Decimal = Field(default=Decimal('0'))
    DiferenciaDia: Decimal = Field(default=Decimal('0'))
    PorcentajeCumplimientoDia: Decimal = Field(default=Decimal('0'))
    
    class Config:
        from_attributes = True


class ResumenRecaudoMes(BaseModel):
    """Resumen de recaudo mensual para gráficos del FE"""
    IDCampanasQA: int
    NombreCampana: str
    IDInversionistaQA: int
    NombreInversionistaQA: str
    AnioMes: str
    TotalRecaudoMes: Decimal = Field(default=Decimal('0'))
    TotalMetaMes: Decimal = Field(default=Decimal('0'))
    DiferenciaMes: Decimal = Field(default=Decimal('0'))
    PorcentajeCumplimientoMes: Decimal = Field(default=Decimal('0'))
    
    class Config:
        from_attributes = True


# Respuestas para API
class RecaudoDiarioResponse(BaseModel):
    """Respuesta para un registro de recaudo"""
    success: bool = True
    data: RecaudoDiarioExtendido
    message: Optional[str] = None


class RecaudoDiarioListResponse(BaseModel):
    """Respuesta para lista de recaudo diario"""
    success: bool = True
    data: List[ResumenRecaudoDia]
    total: int
    filters_applied: Optional[dict] = None


class RecaudoMensualListResponse(BaseModel):
    """Respuesta para lista de recaudo mensual"""
    success: bool = True
    data: List[ResumenRecaudoMes]
    total: int
    filters_applied: Optional[dict] = None
