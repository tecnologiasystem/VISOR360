-- Tabla para gestionar metas mensuales por campaña
USE [LOGS]
GO

CREATE TABLE [dbo].[MetasQA] (
    [IDMeta] INT IDENTITY(1,1) PRIMARY KEY,
    [IDPais] INT NOT NULL, -- Campaña grande (ACC COL, NPL COL, etc) - referencia a tabla 'pais'
    [IDCampana] INT NULL,  -- Subcampaña específica (opcional) - referencia a CampanasQA
    [Mes] INT NOT NULL CHECK (Mes BETWEEN 1 AND 12),
    [Anio] INT NOT NULL CHECK (Anio >= 2020),
    [MontoMeta] DECIMAL(18,2) NOT NULL,
    [FechaCreacion] DATETIME DEFAULT GETDATE(),
    [FechaModificacion] DATETIME DEFAULT GETDATE(),
    [UsuarioCreacion] INT NULL, -- Referencia a UsuariosQA
    
    -- Constraint para evitar metas duplicadas
    CONSTRAINT UQ_Meta_Periodo UNIQUE (IDPais, IDCampana, Mes, Anio)
)
GO

-- Índices para mejorar performance
CREATE INDEX IX_MetasQA_Periodo ON [dbo].[MetasQA] (Anio, Mes)
GO

CREATE INDEX IX_MetasQA_Pais ON [dbo].[MetasQA] (IDPais)
GO

-- Comentarios
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Metas mensuales por campaña grande y/o subcampaña', 
    @level0type = N'SCHEMA', @level0name = 'dbo',
    @level1type = N'TABLE',  @level1name = 'MetasQA'
GO
