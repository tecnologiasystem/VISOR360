-- Script para corregir las restricciones de clave foránea
-- Las FKs apuntan a 'Rol' pero deberían apuntar a 'RolQA'

-- 1. Eliminar las restricciones incorrectas
ALTER TABLE CampanasRolesQA DROP CONSTRAINT FK_CampanasRolesQA_Rol;
ALTER TABLE RolesInversionistasQA DROP CONSTRAINT FK_RolesInversionistasQA_Rol;

-- 2. Recrear las restricciones apuntando a RolQA
ALTER TABLE CampanasRolesQA 
ADD CONSTRAINT FK_CampanasRolesQA_Rol 
FOREIGN KEY (IDRol) REFERENCES RolQA(RolID);

ALTER TABLE RolesInversionistasQA 
ADD CONSTRAINT FK_RolesInversionistasQA_Rol 
FOREIGN KEY (IDRol) REFERENCES RolQA(RolID);

-- Verificar que las restricciones se crearon correctamente
SELECT 
    fk.name AS FK_Name,
    OBJECT_NAME(fk.parent_object_id) AS Child_Table,
    COL_NAME(fc.parent_object_id, fc.parent_column_id) AS Child_Column,
    OBJECT_NAME(fk.referenced_object_id) AS Parent_Table,
    COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS Parent_Column
FROM sys.foreign_keys fk
INNER JOIN sys.foreign_key_columns fc ON fk.object_id = fc.constraint_object_id
WHERE OBJECT_NAME(fk.parent_object_id) IN ('CampanasRolesQA', 'RolesInversionistasQA');
