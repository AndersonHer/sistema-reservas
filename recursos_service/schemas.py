from pydantic import BaseModel
from typing import Optional

class RecursoBase(BaseModel):
    nombre: str
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = "disponible"

class RecursoCreate(RecursoBase):
    pass

class RecursoUpdate(RecursoBase):
    pass

class RecursoOut(RecursoBase):
    id: int

    class Config:
        orm_mode = True
