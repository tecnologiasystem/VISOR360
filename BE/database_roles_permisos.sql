-- Script para crear las tablas de Roles y Permisos Simplificado

-- Tabla de Roles con acceso directo a módulos
CREATE TABLE RolQA (
    RolID INT PRIMARY KEY IDENTITY(1,1),
    NombreRol VARCHAR(100) NOT NULL UNIQUE,
    TorreDeControl BIT NOT NULL DEFAULT 0,  -- 1 = Sí, 0 = No
    Financiero BIT NOT NULL DEFAULT 0,      -- 1 = Sí, 0 = No
    RecursosHumanos BIT NOT NULL DEFAULT 0, -- 1 = Sí, 0 = No
    FechaCreacion DATETIME DEFAULT GETDATE()

);

-- Agregar columna RolID a la tabla Usuario
ALTER TABLE Usuario
ADD RolID INT NULL;

ALTER TABLE Usuario
ADD CONSTRAINT FK_Usuario_Rol FOREIGN KEY (RolID) REFERENCES Rol(RolID);

-- Insertar roles de ejemplo
INSERT INTO Rol (NombreRol, TorreDeControl, Financiero, RecursosHumanos) VALUES
('Administrador', 1, 1, 1),           -- Acceso a todo
('Gerente Financiero', 1, 1, 0),      -- Torre de Control y Financiero
('Gerente RRHH', 0, 0, 1),            -- Solo Recursos Humanos
('Analista Financiero', 1, 0, 0);     -- Solo Torre de Control


-- Tabla de UsuariosQA
CREATE TABLE UsuariosQA (
    IDUsuarioQA INT PRIMARY KEY IDENTITY(1,1),
    NombreUsuarioQA VARCHAR(100) NOT NULL,
    EmailUsuarioQA VARCHAR(150) NOT NULL UNIQUE,
    IDRol INT NOT NULL,
    CONSTRAINT FK_UsuariosQA_Rol FOREIGN KEY (IDRol) REFERENCES Rol(RolID)
);

-- Tabla de CampanasQA
CREATE TABLE CampanasQA (
    IDCampanasQA INT PRIMARY KEY IDENTITY(1,1),
    NombreCampana VARCHAR(100) NOT NULL,
    FechaCreacion DATETIME DEFAULT GETDATE(),
    IDUsuarioLider INT,
    CONSTRAINT FK_CampanasQA_UsuarioLider FOREIGN KEY (IDUsuarioLider) REFERENCES UsuariosQA(IDUsuarioQA)
);

-- Tabla intermedia CampanasRolesQA (muchos a muchos)
CREATE TABLE CampanasRolesQA (
    IDCampanasRolesQA INT PRIMARY KEY IDENTITY(1,1),
    IDCampanasQA INT NOT NULL,
    IDRol INT NOT NULL,
    CONSTRAINT FK_CampanasRolesQA_Campana FOREIGN KEY (IDCampanasQA) REFERENCES CampanasQA(IDCampanasQA),
    CONSTRAINT FK_CampanasRolesQA_Rol FOREIGN KEY (IDRol) REFERENCES Rol(RolID),
    UNIQUE(IDCampanasQA, IDRol)
);

-- Índices para optimizar consultas
CREATE INDEX IX_UsuariosQA_IDRol ON UsuariosQA(IDRol);
CREATE INDEX IX_CampanasRolesQA_IDRol ON CampanasRolesQA(IDRol);
CREATE INDEX IX_CampanasRolesQA_IDCampanasQA ON CampanasRolesQA(IDCampanasQA);

