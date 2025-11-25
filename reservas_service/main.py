from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from reservas_service import crud, schemas
from reservas_service.config.database import Base, engine, get_db

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Reservas")

@app.get("/reservas/", response_model=list[schemas.ReservaResponse])
def listar_reservas(db: Session = Depends(get_db)):
    return crud.obtener_reservas(db)

@app.get("/reservas/{id}", response_model=schemas.ReservaResponse)
def obtener_reserva(id: int, db: Session = Depends(get_db)):
    reserva = crud.obtener_reserva(db, id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

@app.post("/reservas/", response_model=schemas.ReservaResponse)
def crear_reserva_endpoint(reserva: schemas.ReservaCreate, db: Session = Depends(get_db)):
    nueva = crud.crear_reserva(db, reserva)
    if not nueva:
        raise HTTPException(status_code=400, detail="Recurso no disponible en ese horario")
    return nueva

@app.put("/reservas/{id}", response_model=schemas.ReservaResponse)
def modificar_reserva(id: int, data: schemas.ReservaUpdate, db: Session = Depends(get_db)):
    reserva = crud.actualizar_reserva(db, id, data)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

@app.delete("/reservas/{id}")
def cancelar_reserva(id: int, db: Session = Depends(get_db)):
    reserva = crud.eliminar_reserva(db, id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return {"mensaje": "Reserva cancelada exitosamente"}

# Manejo de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Datos inválidos en la solicitud", "errors": exc.errors()},
    )

# Diego lo agrego
@app.get("/reservas/usuario/{usuario_id}/", response_model=list[schemas.ReservaResponse])
def obtener_reservas_usuario(usuario_id: int, db: Session = Depends(get_db)):
    reservas = crud.obtener_reservas_por_usuario(db, usuario_id)
    return reservas