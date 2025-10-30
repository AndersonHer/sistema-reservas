from fastapi import FastAPI
from app.usuarios.routes import router as usuarios_router
from app.recursos.routes import router as recursos_router

app = FastAPI(
    title="Sistema de Reservas",
    description="API para la gestión de reservas, usuarios y recursos.",
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo - Sistema de Reservas",
        "email": "soporte@sistema-reservas.com"
    },
    openapi_tags=[
        {"name": "usuarios", "description": "Operaciones relacionadas con usuarios."},
        {"name": "recursos", "description": "Operaciones CRUD de recursos del sistema (crear, listar, actualizar, eliminar)."},
        {"name": "default", "description": "Operaciones generales del sistema."}
    ]
)

app.include_router(usuarios_router)
app.include_router(recursos_router)

@app.get("/", tags=["default"])
def read_root():
    return {"mensaje": "Sistema de Reservas API", "estado": "activo"}
