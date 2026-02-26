-- Tabla para metas de campañas pequeñas (subcampañas/inversionistas)
-- La suma de estas metas debe dar la meta total del mes para el país

CREATE TABLE metas_campana_pequena (
    id_meta_campana INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Identificación de la campaña
    nombre_pais VARCHAR(100) NOT NULL,  -- 'NPL COL', 'ACC', 'NPL PER', 'NPL CHILE'
    nombre_campana_pequena VARCHAR(100) NOT NULL,  -- 'IFC', 'BANCOMEVA', 'PA', 'TUYA', 'PROPIA', etc.
    
    -- Periodo
    mes INT NOT NULL CHECK (mes BETWEEN 1 AND 12),
    anio INT NOT NULL CHECK (anio >= 2024),
    
    -- Meta
    meta_valor DECIMAL(18, 2) NOT NULL DEFAULT 0,
    
    -- Auditoría
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_modificacion DATETIME DEFAULT GETDATE(),
    usuario_creacion VARCHAR(100),
    usuario_modificacion VARCHAR(100),
    
    -- Índices únicos para evitar duplicados
    CONSTRAINT UQ_meta_campana_pequena_mes UNIQUE (nombre_pais, nombre_campana_pequena, mes, anio)
);

-- Índice para búsquedas por país y mes
CREATE INDEX IX_metas_campana_pequena_pais_mes 
ON metas_campana_pequena (nombre_pais, mes, anio);

-- Índice para búsquedas por campaña pequeña
CREATE INDEX IX_metas_campana_pequena_campana 
ON metas_campana_pequena (nombre_campana_pequena, mes, anio);

-- Datos de ejemplo para diciembre 2025
INSERT INTO metas_campana_pequena (nombre_pais, nombre_campana_pequena, mes, anio, meta_valor)
VALUES 
    -- NPL COL
    ('NPL COL', 'BANCOMEVA', 12, 2025, 150000000),
    ('NPL COL', 'IFC', 12, 2025, 200000000),
    ('NPL COL', 'PA', 12, 2025, 100000000),
    ('NPL COL', 'TUYA', 12, 2025, 250000000),
    
    -- ACC
    ('ACC', 'BANCOLOMBIA', 12, 2025, 300000000),
    
    -- NPL PER
    ('NPL PER', 'IFC', 12, 2025, 100000000),
    ('NPL PER', 'PROPIA', 12, 2025, 80000000),
    
    -- NPL CHILE
    ('NPL CHILE', 'IFC', 12, 2025, 50000000);

-- Vista para verificar que las metas suman correctamente
CREATE VIEW v_metas_consolidadas AS
SELECT 
    nombre_pais,
    mes,
    anio,
    COUNT(*) as cantidad_subcampanas,
    SUM(meta_valor) as meta_total_calculada
FROM metas_campana_pequena
GROUP BY nombre_pais, mes, anio;

-- Query de ejemplo para verificar
-- SELECT * FROM v_metas_consolidadas WHERE mes = 12 AND anio = 2025;
