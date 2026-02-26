-- Script para asignar todas las campañas e inversionistas a todos los roles

-- 1. Obtener todos los roles activos
-- 2. Obtener todas las campañas activas
-- 3. Obtener todos los inversionistas activos
-- 4. Crear las relaciones

-- Limpiar relaciones existentes (opcional - comentar si quieres mantener las actuales)
-- DELETE FROM CampanasRolesQA;
-- DELETE FROM RolesInversionistasQA;

-- Asignar TODAS las campañas a TODOS los roles
INSERT INTO CampanasRolesQA (IDCampanasQA, IDRol)
SELECT c.IDCampanasQA, r.RolID
FROM CampanasQA c
CROSS JOIN RolQA r
INNER JOIN Rol rol ON r.RolID = rol.RolID  -- Solo roles que existen en tabla Rol
WHERE NOT EXISTS (
    SELECT 1 FROM CampanasRolesQA cr 
    WHERE cr.IDCampanasQA = c.IDCampanasQA 
    AND cr.IDRol = r.RolID
);

-- Asignar TODOS los inversionistas a TODOS los roles
INSERT INTO RolesInversionistasQA (IDRol, IDInversionistaQA, FechaCreacion)
SELECT r.RolID, i.IDInversionistaQA, GETDATE()
FROM RolQA r
INNER JOIN Rol rol ON r.RolID = rol.RolID  -- Solo roles que existen en tabla Rol
CROSS JOIN InversionistaQA i
WHERE i.EsActivo = 1
AND NOT EXISTS (
    SELECT 1 FROM RolesInversionistasQA ri 
    WHERE ri.IDRol = r.RolID 
    AND ri.IDInversionistaQA = i.IDInversionistaQA
);

-- Verificar resultados
SELECT 
    r.NombreRol,
    COUNT(DISTINCT cr.IDCampanasQA) as Campanas,
    COUNT(DISTINCT ri.IDInversionistaQA) as Inversionistas
FROM RolQA r
LEFT JOIN CampanasRolesQA cr ON r.RolID = cr.IDRol
LEFT JOIN RolesInversionistasQA ri ON r.RolID = ri.IDRol
GROUP BY r.NombreRol, r.RolID
ORDER BY r.NombreRol;
