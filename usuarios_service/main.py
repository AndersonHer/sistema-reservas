from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from usuarios_service.config.settings import settings
from . import crud, models, schemas
# ====================================================
#  CONEXIÓN A LA BASE DE DATOS
# ====================================================
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

# ====================================================
#  CONFIGURACIÓN DE LA APLICACIÓN FASTAPI
# ====================================================
app = FastAPI(
    title="API de Usuarios",
    version="1.0",
    description="""
    👥 **API REST para la gestión de usuarios**
    
    Esta API permite:
    - Registrar nuevos usuarios  
    - Listar todos los usuarios
    - Obtener usuario por ID
    - Eliminar usuarios
    """,
)

# ====================================================
# 🧩 DEPENDENCIA DE SESIÓN DE BASE DE DATOS
# ====================================================
def get_db():
    """Crea y cierra una sesión de base de datos para cada petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ====================================================
# 1️⃣ REGISTRO DE USUARIO
# ====================================================
@app.post(
    "/usuarios/registro",
    response_model=schemas.UsuarioResponse,
    tags=["Usuarios"],
    summary="Registrar un nuevo usuario",
    description="""
    🧾 **Registra un nuevo usuario en el sistema.**
    
    - Requiere nombre, correo y contraseña.
    - El correo debe ser único.
    - Retorna los datos del usuario registrado.
    """
)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existente = crud.get_user_by_email(db, usuario.email)
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    nuevo = crud.create_user(db, usuario)
    return nuevo

# ====================================================
# 2️⃣ OBTENER TODOS LOS USUARIOS
# ====================================================
@app.get(
    "/usuarios",
    response_model=list[schemas.UsuarioResponse],
    tags=["Usuarios"],
    summary="Obtener todos los usuarios",
    description="""
    📋 **Devuelve una lista de todos los usuarios registrados.**
    """
)
def obtener_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

# ====================================================
# 3️⃣ OBTENER USUARIO POR ID
# ====================================================
@app.get(
    "/usuarios/{id}",
    response_model=schemas.UsuarioResponse,
    tags=["Usuarios"],
    summary="Obtener un usuario por ID",
    description="""
    🔍 **Devuelve la información de un usuario específico.**
    """
)
def obtener_usuario(id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# ====================================================
# 4️⃣ ELIMINAR USUARIO
# ====================================================
@app.delete(
    "/usuarios/{id}",
    tags=["Usuarios"],
    summary="Eliminar un usuario",
    description="""
    🗑️ **Elimina un usuario del sistema.**
    """
)
def eliminar_usuario(id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado correctamente"}

# ====================================================
# 5️⃣ ENDPOINT DE PRUEBA
# ====================================================
@app.get("/")
def root():
    return {"message": "API de Usuarios funcionando correctamente"}