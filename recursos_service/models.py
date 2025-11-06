from sqlalchemy import Column, Integer, String, Enum, Text
from config.database import Base

import enum

class EstadoRecurso(str, enum.Enum):
    disponible = "disponible"
    no_disponible = "no disponible"

class Recurso(Base):
    __tablename__ = "recursos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50))
    descripcion = Column(Text)
    estado = Column(Enum(EstadoRecurso), default=EstadoRecurso.disponible)
