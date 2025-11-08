from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional

class DisponibilidadRequest(BaseModel):
    """ Esquema para la consulta de disponibilidad """
    recurso_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time

class DisponibilidadResponse(BaseModel):
    """ Respuesta de la consulta de disponibilidad """
    disponible: bool
    mensaje: str
    conflicto_id: Optional[int] = None