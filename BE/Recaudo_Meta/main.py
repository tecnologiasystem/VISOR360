"""
Microservicio Recaudo Meta API
FastAPI application para gestión de metas y recaudo por campaña e inversionista
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from config import get_settings
from database import test_connection, DatabaseError
from routers import campana_router, inversionista_router, recaudo_router, carga_router
from routers import recaudos_compat_router, utils_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para la aplicación"""
    # Startup
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Verificar conexión a BD
    if test_connection():
        logger.info("✅ Conexión a base de datos establecida")
    else:
        logger.error("❌ No se pudo conectar a la base de datos")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## API para Gestión de Metas y Recaudo

Esta API provee endpoints para:

### Campañas
- Listar campañas disponibles
- Obtener campañas con sus inversionistas asociados

### Inversionistas
- Listar inversionistas
- Obtener inversionistas por campaña
- Consultar relaciones campaña-inversionista

### Recaudo
- **GET /recaudo/diario**: Resumen de recaudo diario (TipoResumen=1)
- **GET /recaudo/mensual**: Resumen de recaudo mensual (TipoResumen=2)
- **POST /recaudo/carga-excel**: Ejecutar carga desde staging
- CRUD de registros individuales

### Cargas
- Historial de cargas
- Auditoría de cambios

---
**Base de datos**: LOGS (SQL Server)
**Puerto por defecto**: 8001
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Manejador global de errores de base de datos
@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    logger.error(f"Error de base de datos: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error de base de datos",
            "detail": exc.message
        }
    )


# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "detail": str(exc) if settings.DEBUG else "Contacte al administrador"
        }
    )


# Registrar routers
app.include_router(campana_router.router)
app.include_router(inversionista_router.router)
app.include_router(recaudo_router.router)
app.include_router(carga_router.router)
# Routers de compatibilidad con FE existente
app.include_router(recaudos_compat_router.router)
app.include_router(utils_router.router)


# Endpoints de salud y raíz
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz"""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Verificación de salud del servicio"""
    db_status = "connected" if test_connection() else "disconnected"
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION
    }


@app.get("/api/info", tags=["Info"])
async def api_info():
    """Información de la API"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": settings.DB_DATABASE,
        "server": settings.DB_SERVER,
        "endpoints": {
            "campanas": "/campanas",
            "inversionistas": "/inversionistas",
            "recaudo_diario": "/recaudo/diario",
            "recaudo_mensual": "/recaudo/mensual",
            "carga_excel": "/recaudo/carga-excel",
            "cargas": "/cargas",
            "auditoria": "/cargas/auditoria"
        }
    }


# Punto de entrada para ejecución directa
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Iniciando servidor en {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
