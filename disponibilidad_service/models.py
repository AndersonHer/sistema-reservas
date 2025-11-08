from sqlalchemy import Column, Integer, String, Enum, Date, Time

from disponibilidad_service.database import Base 

class Reserva(Base):
    """
    Modelo espejo de Reservas.
    Este servicio solo lo usa para LECTURA.
    """
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True)
    recurso_id = Column(Integer, nullable=False, index=True)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    estado = Column(Enum("activa", "cancelada", name="estado_enum"), default="activa")