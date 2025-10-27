from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Recurso(Base):
    __tablename__ = "recursos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50))
    descripcion = Column(Text)
    estado = Column(Enum('disponible', 'no disponible'), default='disponible')