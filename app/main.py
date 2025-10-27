from fastapi import FastAPI

app = FastAPI(
    title="Sistema de Reservas",
    description="API para gestión de reservas con microservicios",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Sistema de Reservas API", "status": "active"}