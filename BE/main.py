from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers principales
from app.api.usuario_api import router as usuario_router
from app.api.rol_api import router as rol_router
from app.api.campana_api import router as campana_router
from app.api.campanarol_api import router as campanarol_router
from app.api.acuerdo_api import router as acuerdo_router
from app.api.acuerdo_decision_api import router as acuerdo_decision_router
from app.api.acuerdo_obligacion_api import router as acuerdo_obligacion_router
from app.api.acuerdo_pago_api import router as acuerdo_pago_router
from app.api.asignacion_api import router as asignacion_router
from app.api.embudo_api import router as embudo_router
from app.api.marcacion_api import router as marcacion_router
from app.api.recaudo_api import router as recaudo_router
from app.api.calculo_api import router as calculo_router
from app.api.meta_api import router as meta_router
from app.api.meta_campana_api import router as meta_campana_router
from app.api.utils_api import router as utils_router
from app.api.portafolio_api import router as portafolio_router  # Nuevo: API portafolio BD
from app.api.dias_habiles_api import router as dias_habiles_router  # Nuevo: API días hábiles
from app.api.campana_configuracion_api import router as campana_configuracion_router
from app.api.planta_activa_api import router as planta_activa_router  # Nuevo: Radar Talento Humano
from app.api.permisos_api import router as permisos_router  # Nuevo: Gestión de Permisos

# Crear una sola app
app = FastAPI(
    title="SystemGroup API",
    version="1.0",
    description="API principal con módulos de usuarios y gestión :)",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers con prefijo /api
app.include_router(usuario_router, prefix="/api")
app.include_router(rol_router, prefix="/api")
app.include_router(campana_router, prefix="/api")
app.include_router(campanarol_router, prefix="/api")
app.include_router(acuerdo_router, prefix="/api")
app.include_router(acuerdo_decision_router, prefix="/api")
app.include_router(acuerdo_obligacion_router, prefix="/api")
app.include_router(acuerdo_pago_router, prefix="/api")
app.include_router(asignacion_router, prefix="/api")
app.include_router(embudo_router, prefix="/api")
app.include_router(marcacion_router, prefix="/api")
app.include_router(recaudo_router, prefix="/api")
app.include_router(calculo_router, prefix="/api")
app.include_router(meta_router, prefix="/api")
app.include_router(meta_campana_router, prefix="/api")
app.include_router(utils_router, prefix="/api")
app.include_router(portafolio_router, prefix="/api")  # Nuevo: API portafolio BD
app.include_router(dias_habiles_router, prefix="/api")  # Nuevo: API días hábiles
app.include_router(campana_configuracion_router, prefix="/api")  # Nuevo: API configuración días campaña
app.include_router(planta_activa_router, prefix="/api")  # Nuevo: Radar Talento Humano
app.include_router(permisos_router, prefix="/api/permisos", tags=["Permisos"])  # Nuevo: Gestión de Permisos


@app.get("/")
def root():
    return {"message": "Bienvenido a la API de Visor360 🚀"}
