# Sistema de Gestión de Metas por Subcampaña

## Descripción
Sistema que permite definir metas mensuales a nivel de subcampaña (inversionista). La suma de todas las subcampañas da la meta total del país para ese mes.

## Arquitectura

### Base de Datos
**Tabla:** `metas_campana_pequena`

Campos:
- `id_meta_campana`: ID autoincremental
- `nombre_pais`: Nombre del país ('NPL COL', 'ACC', 'NPL PER', 'NPL CHILE')
- `nombre_campana_pequena`: Nombre del inversionista ('IFC', 'BANCOMEVA', 'PA', 'TUYA', etc.)
- `mes`: Mes (1-12)
- `anio`: Año (>= 2024)
- `meta_valor`: Valor de la meta en COP
- Campos de auditoría: fechas y usuarios de creación/modificación

**Vista:** `v_metas_consolidadas`
- Suma automática de metas por país/mes/año
- Útil para validar que la suma sea correcta

### Backend

**DAL:** `BE/app/dal/meta_campana_dal.py`
- `obtener_metas_campana_pequena(nombre_pais, mes, anio)` - Lista todas las metas de subcampañas
- `obtener_meta_total_pais(nombre_pais, mes, anio)` - Suma total de metas del país
- `obtener_meta_campana_especifica(nombre_pais, nombre_campana, mes, anio)` - Meta específica
- `crear_meta_campana(...)` - Crear o actualizar meta (UPSERT)
- `eliminar_meta_campana(...)` - Eliminar meta

**API:** `BE/app/api/meta_campana_api.py`

Endpoints:
- `GET /metas-campana/pais/{nombre_pais}?mes={mes}&anio={anio}`
  - Retorna todas las metas de subcampañas + meta total
  
- `GET /metas-campana/pais/{nombre_pais}/campana/{nombre_campana}?mes={mes}&anio={anio}`
  - Retorna meta de una subcampaña específica
  
- `POST /metas-campana/`
  - Crea o actualiza una meta
  - Body: `{ nombre_pais, nombre_campana, mes, anio, meta_valor, usuario }`
  
- `POST /metas-campana/bulk`
  - Crea o actualiza múltiples metas a la vez
  - Body: Array de objetos de meta
  
- `DELETE /metas-campana/pais/{nombre_pais}/campana/{nombre_campana}?mes={mes}&anio={anio}`
  - Elimina una meta

### Frontend

**Componente:** `FE/src/components/GestionMetas.jsx`

Características:
- Tabla editable con todas las subcampañas del país seleccionado
- Filtros: País, Mes, Año
- InputNumber con formato de moneda COP
- Fila de resumen con total calculado
- Guardar cambios múltiples a la vez (bulk)
- Eliminar metas individuales
- Indicador de cambios sin guardar

**Ruta:** `/gestion-metas`

## Instalación

### 1. Crear tabla en base de datos
Ejecutar el script SQL:
```sql
cd BE/database
-- Ejecutar create_metas_campana_pequena_table.sql en SQL Server
```

### 2. Verificar instalación
```sql
-- Ver datos de ejemplo
SELECT * FROM v_metas_consolidadas WHERE mes = 12 AND anio = 2025;

-- Debería mostrar:
-- NPL COL: 700,000,000 (suma de 4 subcampañas)
-- ACC: 300,000,000 (1 subcampaña)
-- NPL PER: 180,000,000 (2 subcampañas)
-- NPL CHILE: 50,000,000 (1 subcampaña)
```

## Uso

### Definir metas para un mes
1. Ir a `/gestion-metas` en el frontend
2. Seleccionar País, Mes y Año
3. Ingresar valores de meta para cada subcampaña
4. Ver total calculado en la fila de resumen
5. Hacer click en "Guardar Cambios"

### Consultar metas desde código

**Python (Backend):**
```python
from app.dal.meta_campana_dal import obtener_meta_total_pais

meta_total = obtener_meta_total_pais("NPL COL", 12, 2025)
# Retorna: 700000000.0
```

**JavaScript (Frontend):**
```javascript
const response = await api.get('/metas-campana/pais/NPL COL', {
  params: { mes: 12, anio: 2025 }
});
const { meta_total, metas_subcampanas } = response.data;
```

## Integración con Cumplimiento

Para calcular cumplimiento usando estas metas:

1. Obtener recaudo real del mes (ya existente en `recaudo_dal.py`)
2. Obtener meta total del mes (nuevo: `obtener_meta_total_pais()`)
3. Calcular: `cumplimiento = (recaudo_real / meta_total) * 100`

### Por subcampaña:
```python
# Recaudo por subcampaña (ya existe)
recaudo_bancomeva = obtener_recaudo_por_campana_pequena("NPL COL", "BANCOMEVA", 12, 2025)

# Meta de subcampaña (nuevo)
meta_bancomeva = obtener_meta_campana_especifica("NPL COL", "BANCOMEVA", 12, 2025)

# Cumplimiento
cumplimiento = (recaudo_bancomeva / meta_bancomeva) * 100
```

## Validación

El sistema garantiza:
- ✅ Una sola meta por subcampaña/mes/año (constraint UNIQUE)
- ✅ Suma de subcampañas = Meta total del país (vista v_metas_consolidadas)
- ✅ No se pueden crear metas duplicadas
- ✅ Historial de cambios (fechas y usuarios de modificación)

## Subcampañas por País

Según `recaudo_mapping.json`:

- **NPL COL**: BANCOMEVA, IFC, PA, TUYA
- **ACC**: BANCOLOMBIA
- **NPL PER**: IFC, PROPIA
- **NPL CHILE**: IFC

## Próximos Pasos

1. ✅ Crear tabla en base de datos (ejecutar SQL)
2. ✅ Probar API con Postman o desde frontend
3. 🔄 Modificar cálculo de cumplimiento en KpiTablero.jsx para usar metas dinámicas
4. 🔄 Mostrar metas por subcampaña en SeccionCampanias.jsx
5. 🔄 Agregar gráfico de cumplimiento por subcampaña

## Notas Técnicas

- La tabla usa nombres en lugar de IDs para simplificar queries desde Excel
- Los nombres deben coincidir exactamente con los del archivo `recaudo_mapping.json`
- El frontend muestra todas las subcampañas del país, incluso si no tienen meta (valor = 0)
- El bulk insert permite guardar todas las metas de un mes de una sola vez
