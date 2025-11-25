from sqlalchemy.orm import Session
from .models import Reserva
from .schemas import ReservaCreate, ReservaUpdate

def obtener_reservas(db: Session):
    return db.query(Reserva).all()

def obtener_reserva(db: Session, reserva_id: int):
    return db.query(Reserva).filter(Reserva.id == reserva_id).first()

def crear_reserva(db: Session, reserva: ReservaCreate):
    nueva = Reserva(**reserva.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def actualizar_reserva(db: Session, reserva_id: int, data: ReservaUpdate):
    reserva = obtener_reserva(db, reserva_id)
    if not reserva:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(reserva, key, value)
    db.commit()
    db.refresh(reserva)
    return reserva

def eliminar_reserva(db: Session, reserva_id: int):
    reserva = obtener_reserva(db, reserva_id)
    if not reserva:
        return None
    db.delete(reserva)
    db.commit()
    return reserva
# diego
def obtener_reservas_por_usuario(db: Session, usuario_id: int):
    return db.query(Reserva).filter(Reserva.usuario_id == usuario_id).all()