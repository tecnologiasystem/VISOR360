# Torre de Control - Sistema de Lectura de Excel

## Archivos Excel
1. NPL Y ACC COL.xlsx
2. Npl Chile.xlsx  
3. Npl Peru.xlsx

## Filtros por Archivo

### 1. NPL Y ACC COL.xlsx

#### NPL Colombia
- **País:** NPL COL
- **Inversionistas:**
  - BANCOLOMBIA
  - BANCOOMEVA
  - IFC
  - PA
  - TUYA

#### ACC (reemplazar "SYSTEMGROUP COLOMBIA" por "ACC")
- **País:** ACC
- **Inversionistas:**
  - ADAMANTINE
  - ACCION
  - JCAP
  - PRA

### 2. Npl Chile.xlsx

#### NPL Chile
- **Inversionista:** IFC

### 3. Npl Peru.xlsx

#### NPL Perú
- **Inversionistas:**
  - IFC
  - PROPIA

## Funcionalidad

1. Leer archivos Excel
2. Filtrar por:
   - País (campaña grande)
   - Inversionista (sub-campañas)
   - Rango de fechas
3. Sumar columna **RECAUDO**
4. Mostrar resultados en dashboard de Torre de Control

## Próximos Pasos

1. Crear endpoint backend para leer Excel
2. Implementar filtros
3. Crear interfaz frontend
4. Integrar con dashboard existente
