# Recaudo Meta API - Microservicio

## Descripción
Microservicio para gestión de metas y recaudo por campaña e inversionista.
Lee datos de la base de datos SQL Server (LOGS) en lugar de archivos Excel.

## Estructura del proyecto

```
Recaudo_Meta/
├── main.py              # Aplicación FastAPI principal
├── config.py            # Configuración (variables de entorno)
├── database.py          # Conexión a SQL Server con pooling
├── requirements.txt     # Dependencias Python
├── models/              # Modelos Pydantic
│   ├── campana.py       # Modelos para campañas
│   ├── inversionista.py # Modelos para inversionistas
│   ├── recaudo.py       # Modelos para recaudo diario/mensual
│   ├── carga.py         # Modelos para cargas desde Excel
│   └── common.py        # Modelos comunes y respuestas
├── dal/                 # Data Access Layer
│   ├── campana_dal.py   # Acceso a datos de campañas
│   ├── inversionista_dal.py # Acceso a datos de inversionistas
│   ├── recaudo_dal.py   # Acceso a datos de recaudo (incluye SPs)
│   └── carga_dal.py     # Acceso a datos de cargas y staging
├── bll/                 # Business Logic Layer
│   ├── campana_bll.py   # Lógica de negocio de campañas
│   ├── inversionista_bll.py # Lógica de negocio de inversionistas
│   ├── recaudo_bll.py   # Lógica de negocio de recaudo
│   └── carga_bll.py     # Lógica de negocio de cargas
└── routers/             # Endpoints FastAPI
    ├── campana_router.py
    ├── inversionista_router.py
    ├── recaudo_router.py
    └── carga_router.py
```

## Instalación

```bash
cd BE/Recaudo_Meta
pip install -r requirements.txt
```

## Ejecución

```bash
# Desarrollo
python main.py

# Producción
uvicorn main:app --host 0.0.0.0 --port 8001
```

## Endpoints principales

### Campañas
- `GET /campanas` - Lista todas las campañas
- `GET /campanas/{id}` - Obtiene una campaña por ID
- `GET /campanas/con-inversionistas/` - Lista campañas con sus inversionistas

### Inversionistas
- `GET /inversionistas` - Lista todos los inversionistas
- `GET /inversionistas/{id}` - Obtiene un inversionista por ID
- `GET /inversionistas/por-campana/{id_campana}` - Lista inversionistas de una campaña

### Recaudo
- `GET /recaudo/diario` - Resumen de recaudo diario (SP_CampanasRecaudoQA_ConsultaFE TipoResumen=1)
- `GET /recaudo/mensual` - Resumen de recaudo mensual (SP_CampanasRecaudoQA_ConsultaFE TipoResumen=2)
- `POST /recaudo/carga-excel` - Ejecuta carga desde staging (SP_CampanasRecaudoQA_CargarDesdeStaging)
- `GET /recaudo/resumen/por-campana?anio_mes=2025-12` - Resumen por campaña
- `GET /recaudo/resumen/por-inversionista?anio_mes=2025-12` - Resumen por inversionista
- `GET /recaudo/acumulado-diario?anio_mes=2025-12` - Acumulado diario para gráficos

### Cargas
- `GET /cargas` - Historial de cargas
- `GET /cargas/{id}` - Detalle de una carga
- `GET /cargas/{id}/registros` - Registros asociados a una carga
- `GET /cargas/auditoria/` - Auditoría de cambios

## Stored Procedures utilizados

1. **SP_CampanasRecaudoQA_CargarDesdeStaging**
   - Procesa datos del staging
   - Mapea nombres de campañas
   - Hace MERGE sobre CampanasRecaudoDiarioQA

2. **SP_CampanasRecaudoDiarioQA_CRUD**
   - Operaciones CRUD sobre recaudo diario
   - Acciones: 1=INSERT, 2=UPDATE, 3=DELETE, 4=GET, 5=LIST

3. **SP_CampanasRecaudoQA_ConsultaFE**
   - Consultas optimizadas para el frontend
   - TipoResumen=1: Diario
   - TipoResumen=2: Mensual

## Configuración

Variables de entorno (o en config.py):
- `DB_SERVER`: Servidor SQL Server (default: 172.18.72.111)
- `DB_DATABASE`: Base de datos (default: LOGS)
- `DB_USERNAME`: Usuario (default: NEXUM)
- `DB_PASSWORD`: Contraseña
- `PORT`: Puerto del servicio (default: 8001)

## Documentación API

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Base de datos

El servicio usa las siguientes tablas de la BD LOGS:

### Principales
- `CampanasQA` - Catálogo de campañas
- `InversionistaQA` - Catálogo de inversionistas
- `CampanasInversionistasQA` - Relación N:N campaña-inversionista
- `CampanasRecaudoDiarioQA` - Recaudo y meta por día hábil

### Carga y auditoría
- `CampanasRecaudoStagingQA` - Staging para carga desde Excel
- `CampanasRecaudoCargaQA` - Registro de cargas
- `CampanasRecaudoAuditoriaQA` - Auditoría de cambios (trigger automático)

## Ejemplo de uso desde el FE

```javascript
// Obtener recaudo mensual de últimos 3 meses
const response = await fetch(
  'http://localhost:8001/recaudo/mensual?' +
  'anio_mes_desde=2025-10&anio_mes_hasta=2025-12'
);
const data = await response.json();

// Obtener resumen por campaña para un mes
const resumen = await fetch(
  'http://localhost:8001/recaudo/resumen/por-campana?anio_mes=2025-12'
);
```
