"""
Modelos Pydantic para Campañas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CampanaBase(BaseModel):
    """Modelo base de Campaña"""
    NombreCampana: str = Field(..., max_length=100, description="Nombre de la campaña")


class CampanaCreate(CampanaBase):
    """Modelo para crear una Campaña"""
    IDUsuarioLider: Optional[int] = Field(None, description="ID del usuario líder")


class Campana(CampanaBase):
    """Modelo completo de Campaña"""
    IDCampanasQA: int = Field(..., description="ID único de la campaña")
    FechaCreacion: datetime = Field(..., description="Fecha de creación")
    IDUsuarioLider: Optional[int] = Field(None, description="ID del usuario líder")
    
    class Config:
        from_attributes = True


class CampanaSimple(BaseModel):
    """Modelo simplificado para selectores en FE"""
    IDCampanasQA: int
    NombreCampana: str
    
    class Config:
        from_attributes = True


class CampanaRol(BaseModel):
    """Relación Campaña-Rol"""
    IDCampanasRolesQA: int
    IDCampanasQA: int
    IDRol: int
    
    class Config:
        from_attributes = True


class CampanaListResponse(BaseModel):
    """Respuesta para lista de campañas"""
    success: bool = True
    data: List[CampanaSimple]
    total: int
