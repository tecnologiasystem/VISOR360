-- Crear tabla para relacionar Roles con Inversionistas específicos
-- Esto permite que un rol tenga acceso solo a inversionistas seleccionados

-- Verificar si la tabla ya existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'RolesInversionistasQA')
BEGIN
    CREATE TABLE RolesInversionistasQA (
        IDRolInversionista INT IDENTITY(1,1) PRIMARY KEY,
        IDRol INT NOT NULL,
        IDInversionistaQA INT NOT NULL,
        FechaCreacion DATETIME DEFAULT GETDATE(),
        
        -- Foreign Keys
        CONSTRAINT FK_RolesInversionistas_Rol 
            FOREIGN KEY (IDRol) REFERENCES RolQA(RolID),
        CONSTRAINT FK_RolesInversionistas_Inversionista 
            FOREIGN KEY (IDInversionistaQA) REFERENCES InversionistaQA(IDInversionistaQA),
        
        -- Constraint único para evitar duplicados
        CONSTRAINT UQ_RolInversionista 
            UNIQUE (IDRol, IDInversionistaQA)
    );
    
    PRINT 'Tabla RolesInversionistasQA creada exitosamente';
END
ELSE
BEGIN
    PRINT 'La tabla RolesInversionistasQA ya existe';
END

GO

-- Crear índices para mejorar rendimiento
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_RolesInversionistas_Rol')
BEGIN
    CREATE INDEX IX_RolesInversionistas_Rol 
    ON RolesInversionistasQA(IDRol);
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_RolesInversionistas_Inversionista')
BEGIN
    CREATE INDEX IX_RolesInversionistas_Inversionista 
    ON RolesInversionistasQA(IDInversionistaQA);
END

GO
