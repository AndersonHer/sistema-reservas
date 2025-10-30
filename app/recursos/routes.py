# app/recursos/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud
from app.usuarios.models import get_db

router = APIRouter(
    prefix="/recursos",
    tags=["recursos"],
    responses={404: {"description": "No encontrado"}}
)

# ------------------- FUNCIONES CRUD -------------------

@router.get("/", response_model=List[schemas.RecursoSalida], summary="Listar recursos")
def listar_recursos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recursos = crud.listar_recursos(db, skip=skip, limit=limit)
    print("📘 [GET] /recursos/ → Se listaron todos los recursos correctamente.")
    return recursos


@router.get("/{recurso_id}", response_model=schemas.RecursoSalida, summary="Obtener recurso por ID")
def obtener_recurso(recurso_id: int, db: Session = Depends(get_db)):
    recurso = crud.obtener_recurso(db, recurso_id)
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    print(f"🔍 [GET] /recursos/{recurso_id} → Se consultó un recurso por su ID correctamente.")
    return recurso


@router.post("/", response_model=schemas.RecursoSalida, summary="Crear recurso")
def crear_recurso(recurso: schemas.RecursoCrear, db: Session = Depends(get_db)):
    nuevo = crud.crear_recurso(db, recurso)
    print("🟢 [POST] /recursos/ → Se creó un nuevo recurso correctamente.")
    return nuevo


@router.put("/{recurso_id}", response_model=schemas.RecursoSalida, summary="Actualizar recurso")
def actualizar_recurso(recurso_id: int, datos: schemas.RecursoActualizar, db: Session = Depends(get_db)):
    actualizado = crud.actualizar_recurso(db, recurso_id, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    print(f"🟡 [PUT] /recursos/{recurso_id} → Se actualizó un recurso existente correctamente.")
    return actualizado


@router.delete("/{recurso_id}", summary="Eliminar recurso")
def eliminar_recurso(recurso_id: int, db: Session = Depends(get_db)):
    eliminado = crud.eliminar_recurso(db, recurso_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    print(f"🔴 [DELETE] /recursos/{recurso_id} → Se eliminó un recurso exitosamente.")
    return {"mensaje": "Recurso eliminado correctamente"}
