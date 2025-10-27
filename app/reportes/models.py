from sqlalchemy import Column, Integer, String, Date, Time, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class HistorialReserva(Base):
    __tablename__ = "historial_reservas"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey('reservas.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    recurso_id = Column(Integer, ForeignKey('recursos.id'), nullable=False)
    fecha_reserva = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    accion = Column(String(50), nullable=False)
    fecha_registro = Column(TIMESTAMP, default='CURRENT_TIMESTAMP')