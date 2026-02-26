# Main file para correr la versión que lee desde Nueva Data.xlsx
# Se ejecuta en puerto 8003 para comparar con la versión original en puerto 8002

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar los routers de nueva data
from app.api import recaudo_api_nueva_data, meta_campana_api_nueva_data

# Importar routers que no cambian (usuario, etc.)
from app.api.usuario_api import router as usuario_router
from app.api.rol_api import router as rol_router
from app.api.campana_api import router as campana_router
from app.api.utils_api import router as utils_router

app = FastAPI(
    title="QA Dashboard API - Nueva Data Version",
    version="2.0.0",
    description="API que lee recaudos y metas desde Nueva Data.xlsx (archivo consolidado)",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers de nueva data
app.include_router(recaudo_api_nueva_data.router, prefix="/api")
app.include_router(meta_campana_api_nueva_data.router, prefix="/api")

# Registrar routers que no cambian
app.include_router(usuario_router, prefix="/api")
app.include_router(rol_router, prefix="/api")
app.include_router(campana_router, prefix="/api")
app.include_router(utils_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "QA Dashboard API - Nueva Data Version",
        "version": "2.0.0",
        "data_source": "Nueva Data.xlsx (consolidated file)",
        "port": 8001,
    }
