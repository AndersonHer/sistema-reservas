# app/recursos/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class RecursoBase(BaseModel):
    nombre: str = Field(..., example="Sala de Conferencias")
    tipo: Optional[str] = Field(None, example="sala")
    descripcion: Optional[str] = Field(None, example="Sala equipada con proyector")
    estado: Optional[str] = Field("disponible", example="disponible")

class RecursoCrear(RecursoBase):
    pass

class RecursoActualizar(BaseModel):
    nombre: Optional[str]
    tipo: Optional[str]
    descripcion: Optional[str]
    estado: Optional[str]

class RecursoSalida(BaseModel):
    id: int
    nombre: str
    tipo: Optional[str]
    descripcion: Optional[str]
    estado: Optional[str]

    class Config:
        from_attributes = True
