-- Script para poblar datos de ejemplo en las tablas de permisos
-- Ejecutar después de crear las tablas con database_roles_permisos.sql

USE LOGS;
GO

-- ==================== LIMPIAR DATOS EXISTENTES (OPCIONAL) ====================
-- Descomentar si quieres empezar desde cero

-- DELETE FROM CampanasRolesQA;
-- DELETE FROM CampanasInversionistasQA;
-- DELETE FROM UsuariosQA;
-- DELETE FROM CampanasQA;
-- DELETE FROM InversionistaQA;
-- DELETE FROM RolQA;
-- GO

-- ==================== INSERTAR ROLES ====================

SET IDENTITY_INSERT RolQA ON;

INSERT INTO RolQA (RolID, NombreRol, TorreDeControl, Financiero, RecursosHumanos)
VALUES
(1, 'Administrador', 1, 1, 1),           -- Acceso completo
(2, 'Gerente Torre Control', 1, 0, 0),   -- Solo Torre de Control
(3, 'Gerente Financiero', 1, 1, 0),      -- Torre + Financiero
(4, 'Gerente RRHH', 0, 0, 1),            -- Solo RRHH
(5, 'Analista', 1, 0, 0);                -- Solo visualización Torre

SET IDENTITY_INSERT RolQA OFF;
GO

-- ==================== INSERTAR USUARIOS ====================

SET IDENTITY_INSERT UsuariosQA ON;

INSERT INTO UsuariosQA (IDUsuarioQA, NombreUsuarioQA, EmailUsuarioQA, IDRol)
VALUES
(35, 'Juan Camilo Castillo', 'j.castillo@gnpl.com', 1),
(41, 'Edilma Fontecha', 'e.fontecha@gnpl.com', 3);

SET IDENTITY_INSERT UsuariosQA OFF;
GO

-- ==================== INSERTAR CAMPAÑAS ====================

SET IDENTITY_INSERT CampanasQA ON;

INSERT INTO CampanasQA (IDCampanasQA, NombreCampana, IDUsuarioLider)
VALUES
(1, 'NPL COL', 35),
(2, 'ACC', 35);

SET IDENTITY_INSERT CampanasQA OFF;
GO

-- ==================== INSERTAR INVERSIONISTAS ====================

SET IDENTITY_INSERT InversionistaQA ON;

-- Inversionistas NPL COL
INSERT INTO InversionistaQA (IDInversionistaQA, NombreInversionistaQA, EsActivo)
VALUES
(1, 'BANCOOMEVA', 1),
(2, 'IFC', 1),
(3, 'CREDIVALORES', 1),
(4, 'PA', 1),
(5, 'TUYA', 1);

-- Inversionistas ACC
INSERT INTO InversionistaQA (IDInversionistaQA, NombreInversionistaQA, EsActivo)
VALUES
(6, 'ACCION', 1),
(7, 'ADAMANTINE', 1),
(8, 'INTERASEO', 1),
(9, 'JCAP', 1),
(10, 'PRA', 1),
(11, 'GERENTE', 1);

SET IDENTITY_INSERT InversionistaQA OFF;
GO

-- ==================== ASIGNAR INVERSIONISTAS A CAMPAÑAS ====================

SET IDENTITY_INSERT CampanasInversionistasQA ON;

-- NPL COL
INSERT INTO CampanasInversionistasQA (IDCampanasInversionistasQA, IDCampanasQA, IDInversionistaQA)
VALUES
(1, 1, 1),  -- BANCOOMEVA
(2, 1, 2),  -- IFC
(3, 1, 3),  -- CREDIVALORES
(4, 1, 4),  -- PA
(5, 1, 5);  -- TUYA

-- ACC
INSERT INTO CampanasInversionistasQA (IDCampanasInversionistasQA, IDCampanasQA, IDInversionistaQA)
VALUES
(6, 2, 6),   -- ACCION
(7, 2, 7),   -- ADAMANTINE
(8, 2, 8),   -- INTERASEO
(9, 2, 9),   -- JCAP
(10, 2, 10), -- PRA
(11, 2, 11); -- GERENTE

SET IDENTITY_INSERT CampanasInversionistasQA OFF;
GO

-- ==================== ASIGNAR CAMPAÑAS A ROLES ====================

SET IDENTITY_INSERT CampanasRolesQA ON;

-- Administrador (Rol 1) - Acceso a todas las campañas
INSERT INTO CampanasRolesQA (IDCampanasRolesQA, IDCampanasQA, IDRol)
VALUES
(1, 1, 1),  -- NPL COL
(2, 2, 1);  -- ACC

-- Gerente Torre Control (Rol 2) - Solo NPL COL
INSERT INTO CampanasRolesQA (IDCampanasRolesQA, IDCampanasQA, IDRol)
VALUES
(3, 1, 2);  -- NPL COL

-- Gerente Financiero (Rol 3) - Acceso a todas
INSERT INTO CampanasRolesQA (IDCampanasRolesQA, IDCampanasQA, IDRol)
VALUES
(4, 1, 3),  -- NPL COL
(5, 2, 3);  -- ACC

SET IDENTITY_INSERT CampanasRolesQA OFF;
GO

-- ==================== VERIFICACIÓN ====================

PRINT '========== VERIFICACIÓN DE DATOS ==========';
PRINT '';

PRINT 'Roles creados:';
SELECT RolID, NombreRol, TorreDeControl, Financiero, RecursosHumanos FROM RolQA;
PRINT '';

PRINT 'Usuarios creados:';
SELECT u.IDUsuarioQA, u.NombreUsuarioQA, u.EmailUsuarioQA, r.NombreRol
FROM UsuariosQA u
LEFT JOIN RolQA r ON u.IDRol = r.RolID;
PRINT '';

PRINT 'Campañas creadas:';
SELECT c.IDCampanasQA, c.NombreCampana, u.NombreUsuarioQA as Lider
FROM CampanasQA c
LEFT JOIN UsuariosQA u ON c.IDUsuarioLider = u.IDUsuarioQA;
PRINT '';

PRINT 'Inversionistas por campaña:';
SELECT 
    c.NombreCampana,
    i.NombreInversionistaQA
FROM CampanasInversionistasQA ci
INNER JOIN CampanasQA c ON ci.IDCampanasQA = c.IDCampanasQA
INNER JOIN InversionistaQA i ON ci.IDInversionistaQA = i.IDInversionistaQA
ORDER BY c.NombreCampana, i.NombreInversionistaQA;
PRINT '';

PRINT 'Campañas asignadas a roles:';
SELECT 
    r.NombreRol,
    c.NombreCampana
FROM CampanasRolesQA cr
INNER JOIN RolQA r ON cr.IDRol = r.RolID
INNER JOIN CampanasQA c ON cr.IDCampanasQA = c.IDCampanasQA
ORDER BY r.NombreRol, c.NombreCampana;

PRINT '';
PRINT '========== DATOS INSERTADOS CORRECTAMENTE ==========';

GO
