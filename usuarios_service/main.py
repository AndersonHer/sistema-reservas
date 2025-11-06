from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine



from usuarios_service.config.settings import settings


from . import crud, models, schemas
from . import auth


# ====================================================
# 🚀 CONEXIÓN A LA BASE DE DATOS
# ====================================================
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)


# ====================================================
# ⚙️ CONFIGURACIÓN DE LA APLICACIÓN FASTAPI
# ====================================================
app = FastAPI(
    title="API de Usuarios",
    version="1.0",
    description="""
    🔐 **API REST para la gestión de usuarios**
    
    Esta API permite:
    - Registrar nuevos usuarios  
    - Iniciar sesión (Login con JWT)  
    - Obtener el perfil del usuario autenticado  
    - Consultar información de usuarios (solo admin)
    """,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


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
    
    - Requiere nombre, correo, contraseña y rol.
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
# 2️⃣ LOGIN DE USUARIO
# ====================================================
@app.post(
    "/usuarios/login",
    response_model=schemas.Token,
    tags=["Autenticación"],
    summary="Iniciar sesión (Login)",
    description="""
    🔑 **Autenticación de usuario mediante correo y contraseña.**
    
    - Retorna un *token JWT* válido.
    - Este token se usa para acceder a rutas protegidas (`/usuarios/me`, `/usuarios/{id}`, etc.).
    """
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    token = auth.create_access_token({"sub": str(user.id), "rol": user.rol})
    return {"access_token": token, "token_type": "bearer"}


# ====================================================
# 3️⃣ OBTENER USUARIO ACTUAL
# ====================================================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtiene el usuario autenticado a partir del token JWT."""
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    user_id = int(payload.get("sub"))
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@app.get(
    "/usuarios/me",
    response_model=schemas.UsuarioResponse,
    tags=["Usuarios"],
    summary="Obtener perfil del usuario autenticado",
    description="""
    👤 **Devuelve la información del usuario autenticado.**
    
    - Requiere estar logueado.
    - Muestra tu propio perfil según el token JWT.
    """
)
def perfil_usuario(current_user=Depends(get_current_user)):
    return current_user


# ====================================================
# 4️⃣ OBTENER USUARIO POR ID (PROTEGIDO POR ROL)
# ====================================================
@app.get(
    "/usuarios/{id}",
    response_model=schemas.UsuarioResponse,
    tags=["Usuarios"],
    summary="Obtener un usuario por ID (solo admin o el mismo usuario)",
    description="""
    🔍 **Devuelve la información de un usuario específico.**
    
    - Si eres *admin*, puedes ver cualquier usuario.  
    - Si eres *usuario*, solo puedes ver tu propio perfil.  
    - Requiere autenticación con token JWT.
    """
)
def obtener_usuario(id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    # 🔒 Verificación de permisos
    if current_user.rol != "admin" and current_user.id != id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver otros usuarios"
        )

    user = crud.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
