from sqlalchemy.orm import Session
from .models import Usuario
from .auth import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(Usuario).filter(Usuario.id == user_id).first()

def create_user(db: Session, user_data):
    nuevo_usuario = Usuario(
        nombre=user_data.nombre,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        rol="usuario",
        activo=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario
