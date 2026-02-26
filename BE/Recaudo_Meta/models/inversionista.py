"""
Modelos Pydantic para Inversionistas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InversionistaBase(BaseModel):
    """Modelo base de Inversionista"""
    NombreInversionistaQA: str = Field(..., max_length=100, description="Nombre del inversionista")


class InversionistaCreate(InversionistaBase):
    """Modelo para crear un Inversionista"""
    IDUsuarioCreacion: int = Field(..., description="ID del usuario que crea")


class Inversionista(InversionistaBase):
    """Modelo completo de Inversionista"""
    IDInversionistaQA: int = Field(..., description="ID único del inversionista")
    EsActivo: bool = Field(True, description="Si está activo")
    FechaCreacion: datetime = Field(..., description="Fecha de creación")
    IDUsuarioCreacion: int = Field(..., description="ID del usuario que creó")
    
    class Config:
        from_attributes = True


class InversionistaSimple(BaseModel):
    """Modelo simplificado para selectores en FE"""
    IDInversionistaQA: int
    NombreInversionistaQA: str
    EsActivo: bool = True
    
    class Config:
        from_attributes = True


class InversionistaListResponse(BaseModel):
    """Respuesta para lista de inversionistas"""
    success: bool = True
    data: List[InversionistaSimple]
    total: int


# Relación Campaña-Inversionista
class CampanaInversionistaBase(BaseModel):
    """Modelo base para relación Campaña-Inversionista"""
    IDCampanasQA: int = Field(..., description="ID de la campaña")
    IDInversionistaQA: int = Field(..., description="ID del inversionista")


class CampanaInversionistaCreate(CampanaInversionistaBase):
    """Modelo para crear relación"""
    IDUsuarioCreacion: int = Field(..., description="ID del usuario que crea")


class CampanaInversionista(CampanaInversionistaBase):
    """Modelo completo de relación Campaña-Inversionista"""
    IDCampanasInversionistasQA: int = Field(..., description="ID único de la relación")
    EsActivo: bool = Field(True, description="Si está activa")
    FechaCreacion: datetime = Field(..., description="Fecha de creación")
    IDUsuarioCreacion: int = Field(..., description="ID del usuario que creó")
    
    # Campos extendidos (para joins)
    NombreCampana: Optional[str] = None
    NombreInversionistaQA: Optional[str] = None
    
    class Config:
        from_attributes = True


class CampanaInversionistaSimple(BaseModel):
    """Modelo simplificado"""
    IDCampanasInversionistasQA: int
    IDCampanasQA: int
    NombreCampana: str
    IDInversionistaQA: int
    NombreInversionistaQA: str
    
    class Config:
        from_attributes = True
