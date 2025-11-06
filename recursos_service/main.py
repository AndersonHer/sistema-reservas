from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine, Base

import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Recursos")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/recursos/", response_model=list[schemas.RecursoOut])
def listar_recursos(db: Session = Depends(get_db)):
    return crud.get_recursos(db)

@app.get("/recursos/{id}", response_model=schemas.RecursoOut)
def obtener_recurso(id: int, db: Session = Depends(get_db)):
    recurso = crud.get_recurso(db, id)
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return recurso

@app.post("/recursos/", response_model=schemas.RecursoOut)
def crear_recurso(recurso: schemas.RecursoCreate, db: Session = Depends(get_db)):
    return crud.create_recurso(db, recurso)

@app.put("/recursos/{id}", response_model=schemas.RecursoOut)
def actualizar_recurso(id: int, recurso: schemas.RecursoUpdate, db: Session = Depends(get_db)):
    db_recurso = crud.update_recurso(db, id, recurso)
    if not db_recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return db_recurso

@app.delete("/recursos/{id}")
def eliminar_recurso(id: int, db: Session = Depends(get_db)):
    ok = crud.delete_recurso(db, id)
    if not ok:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return {"mensaje": "Recurso eliminado correctamente"}
