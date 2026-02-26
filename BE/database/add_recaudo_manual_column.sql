-- Agregar columna para recaudo manual de Interaseo
-- Este recaudo manual se usará en Torre de Control cuando no haya data en BD

ALTER TABLE metas_campana_pequena
ADD recaudo_manual DECIMAL(18, 2) NULL DEFAULT 0;

-- Comentario: Esta columna almacena el recaudo manual de subcampañas como Interaseo
-- que no tienen data en la BD. Puede ser valor mensual o diario según configuración.

GO

-- Actualizar registros existentes
UPDATE metas_campana_pequena
SET recaudo_manual = 0
WHERE recaudo_manual IS NULL;

GO
