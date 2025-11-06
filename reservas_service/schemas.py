from pydantic import BaseModel
from datetime import date, time

class ReservaBase(BaseModel):
    usuario_id: int
    recurso_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    fecha: date | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None

class ReservaResponse(ReservaBase):
    id: int
    estado: str

    class Config:
        from_attributes = True  # Reemplaza orm_mode en Pydantic v2
