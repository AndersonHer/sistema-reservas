# app/recursos/models.py
from sqlalchemy import Column, Integer, String, Text, Enum
from app.usuarios.models import Base, engine  # reutilizamos la Base global

class Recurso(Base):
    __tablename__ = "recursos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=True)
    descripcion = Column(Text, nullable=True)
    # Coincide con tu base: enum('disponible','no disponible')
    estado = Column(
        Enum('disponible', 'no disponible', name='estado_recurso'),
        nullable=True,
        default='disponible'
    )

# Solo crea si no existe (no altera otras tablas)
Base.metadata.create_all(bind=engine)

