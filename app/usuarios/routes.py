# app/usuarios/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, crud, auth, schemas
from .auth import get_current_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/registro", response_model=schemas.UsuarioSalida, summary="Registrar usuario")
def registro(usuario_in: schemas.UsuarioCrear, db: Session = Depends(models.get_db)):
    """
    Registra un nuevo usuario en el sistema.
    Si el correo ya existe, devuelve un error 400.
    """
    try:
        creado = crud.crear_usuario(db, usuario_in)
        if creado is None:
            # 💡 Ahora devolvemos error 400 directamente, sin caer en el except
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El correo '{usuario_in.correo}' ya está registrado en el sistema."
            )
        print(f"✅ Usuario registrado correctamente: {usuario_in.correo}")
        return creado
    except HTTPException:
        # ⚠️ Si ya se lanzó un HTTPException, la dejamos pasar sin capturarla
        raise
    except Exception as e:
        print("❌ ERROR EN REGISTRO:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en el servidor. Contacte al administrador."
        )

@router.post("/login", response_model=schemas.Token, summary="Inicio de sesión")
def login(data: schemas.UsuarioIniciarSesion, db: Session = Depends(models.get_db)):
    """
    Autentica al usuario y devuelve un token JWT válido.
    Si las credenciales no son correctas, devuelve un error 401.
    """
    try:
        usuario = crud.autenticar_usuario(db, data.correo, data.contrasena)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas. Verifique su correo y contraseña."
            )
        token = auth.create_access_token({"sub": str(usuario.id), "rol": usuario.rol})
        print(f"🔐 Usuario autenticado correctamente: {usuario.correo}")
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print("❌ ERROR EN LOGIN:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al intentar autenticar. Contacte al administrador."
        )

@router.get("/{user_id}", response_model=schemas.UsuarioSalida, summary="Obtener usuario por ID")
def obtener_usuario(user_id: int, db: Session = Depends(models.get_db)):
    """
    Devuelve la información pública de un usuario por su ID.
    Si no existe, devuelve un error 404.
    """
    try:
        user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        print(f"ℹ️ Usuario consultado por ID: {user_id}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        print("❌ ERROR AL OBTENER USUARIO:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al consultar el usuario."
        )

@router.get("/me", response_model=schemas.UsuarioSalida, summary="Mi perfil (protegido)")
def obtener_usuario_actual(user = Depends(get_current_user)):
    """
    Devuelve la información del usuario autenticado usando el token JWT.
    """
    try:
        print(f"👤 Perfil consultado: {user.correo}")
        return user
    except Exception as e:
        print("❌ ERROR EN /me:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener el perfil del usuario autenticado."
        )
