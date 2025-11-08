from sqlalchemy.orm import Session
from sqlalchemy import and_
from disponibilidad_service.models import Reserva  # <-- Importación absoluta
from datetime import date, time

def check_disponibilidad(db: Session, recurso_id: int, fecha: date, hora_inicio: time, hora_fin: time):
    """
    Verifica si existe un choque de horario para un recurso en una fecha/hora.
    
    Lógica de solapamiento:
    (StartA < EndB) AND (EndA > StartB)
    """
    
    conflicto = db.query(Reserva).filter(
        Reserva.recurso_id == recurso_id,
        Reserva.fecha == fecha,
        Reserva.estado == 'activa',
        and_(
            Reserva.hora_inicio < hora_fin,  
            Reserva.hora_fin > hora_inicio    
        )
    ).first()

    if conflicto:
        # choco
        return {
            "disponible": False,
            "mensaje": f"Conflicto de horario. El recurso ya está reservado (ID Reserva: {conflicto.id}).",
            "conflicto_id": conflicto.id
        }
    else:
        # No choca el perro
        return {
            "disponible": True,
            "mensaje": "El recurso está disponible en este horario.",
            "conflicto_id": None
        }