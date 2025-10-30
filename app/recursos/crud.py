# app/recursos/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def listar_recursos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Recurso).offset(skip).limit(limit).all()

def obtener_recurso(db: Session, recurso_id: int):
    return db.query(models.Recurso).filter(models.Recurso.id == recurso_id).first()

def crear_recurso(db: Session, recurso: schemas.RecursoCrear):
    nuevo = models.Recurso(
        nombre=recurso.nombre,
        tipo=recurso.tipo,
        descripcion=recurso.descripcion,
        estado=recurso.estado or "disponible"
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def actualizar_recurso(db: Session, recurso_id: int, datos: schemas.RecursoActualizar):
    recurso = obtener_recurso(db, recurso_id)
    if not recurso:
        return None
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(recurso, key, value)
    db.commit()
    db.refresh(recurso)
    return recurso

def eliminar_recurso(db: Session, recurso_id: int):
    recurso = obtener_recurso(db, recurso_id)
    if not recurso:
        return None
    db.delete(recurso)
    db.commit()
    return recurso
