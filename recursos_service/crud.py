from sqlalchemy.orm import Session
from models import Recurso
from schemas import RecursoCreate, RecursoUpdate

def get_recursos(db: Session):
    return db.query(Recurso).all()

def get_recurso(db: Session, recurso_id: int):
    return db.query(Recurso).filter(Recurso.id == recurso_id).first()

def create_recurso(db: Session, recurso: RecursoCreate):
    db_recurso = Recurso(**recurso.dict())
    db.add(db_recurso)
    db.commit()
    db.refresh(db_recurso)
    return db_recurso

def update_recurso(db: Session, recurso_id: int, recurso: RecursoUpdate):
    db_recurso = get_recurso(db, recurso_id)
    if not db_recurso:
        return None
    for key, value in recurso.dict(exclude_unset=True).items():
        setattr(db_recurso, key, value)
    db.commit()
    db.refresh(db_recurso)
    return db_recurso

def delete_recurso(db: Session, recurso_id: int):
    db_recurso = get_recurso(db, recurso_id)
    if db_recurso:
        db.delete(db_recurso)
        db.commit()
        return True
    return False
