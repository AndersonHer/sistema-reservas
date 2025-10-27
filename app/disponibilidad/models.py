from sqlalchemy import Column, Integer, Date, Time, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Disponibilidad(Base):
    __tablename__ = "disponibilidad"

    id = Column(Integer, primary_key=True, index=True)
    recurso_id = Column(Integer, ForeignKey('recursos.id'), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    disponible = Column(Boolean, default=True)