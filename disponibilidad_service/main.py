from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, time

from disponibilidad_service.database import engine, Base, get_db
from disponibilidad_service import crud, schemas

app = FastAPI(
    title="API de Disponibilidad",  #
    version="1.0",
    description="""
    ✅ **API REST para la consulta de disponibilidad.**
    
    Permite verificar si un recurso tiene choques de horario
    antes de crear o modificar una reserva.
    """,
)

@app.get(
    "/disponibilidad/check",  #
    response_model=schemas.DisponibilidadResponse,
    tags=["Disponibilidad"],
    summary="Verificar disponibilidad de un recurso",
    description="""
    Comprueba si un recurso específico está disponible en una fecha y
    rango de horas determinado.
    
    La lógica detecta cualquier solapamiento (choque) con reservas
    que ya existan y estén 'activas'.
    """
)
def verificar_disponibilidad(
    recurso_id: int = Query(..., description="ID del recurso a verificar"),
    fecha: date = Query(..., description="Fecha de la consulta (YYYY-MM-DD)"),
    hora_inicio: time = Query(..., description="Hora de inicio (HH:MM:SS)"),
    hora_fin: time = Query(..., description="Hora de fin (HH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """
    Endpoint principal para chequear la disponibilidad.
    """
    if hora_inicio >= hora_fin:
        raise HTTPException(
            status_code=400,
            detail="La hora de inicio debe ser anterior a la hora de fin."
        )
        
   
    resultado = crud.check_disponibilidad(db, recurso_id, fecha, hora_inicio, hora_fin)
    
    return resultado

@app.get("/")
def read_root():
    return {"message": "API de Disponibilidad funcionando"}