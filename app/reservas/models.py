from sqlalchemy import Column, Integer, Date, Time, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    recurso_id = Column(Integer, ForeignKey('recursos.id'), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(Enum('activa', 'cancelada'), default='activa')

    # Relaciones
    usuario = relationship("Usuario", backref="reservas")
    recurso = relationship("Recurso", backref="reservas")