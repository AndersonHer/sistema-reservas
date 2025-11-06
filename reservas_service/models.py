from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from .config.database import Base

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    recurso_id = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(Enum("activa", "cancelada", name="estado_enum"), default="activa")