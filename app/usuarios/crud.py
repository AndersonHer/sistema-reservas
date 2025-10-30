# app/usuarios/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models, schemas
from .auth import get_password_hash, verify_password

def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    """
    Crea un nuevo usuario. Recibe un Pydantic schema UsuarioCrear.
    Retorna el objeto Usuario (ORM) o None si ya existe el correo o hay error.
    """
    try:
        # Verificar si el correo ya existe
        existente = db.query(models.Usuario).filter(models.Usuario.correo == usuario.correo).first()
        if existente:
            print("⚠️ El correo ya existe:", usuario.correo)
            return None

        # ⚙️ Asegurar máximo de 72 bytes para bcrypt (evitar error)
        contrasena_bytes = usuario.contrasena.encode("utf-8")
        contrasena_truncada = contrasena_bytes[:72].decode("utf-8", "ignore")

        # Encriptar contraseña
        hashed = get_password_hash(contrasena_truncada)

        # Crear instancia del nuevo usuario
        nuevo = models.Usuario(
            nombre=usuario.nombre.strip(),
            correo=usuario.correo.strip().lower(),
            contrasena=hashed,
            rol="usuario"
        )

        # Guardar en la base de datos
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)

        print(f"✅ Usuario registrado correctamente: {nuevo.correo}")
        return nuevo

    except SQLAlchemyError as e:
        # Si ocurre un error en la BD, revertimos y mostramos el mensaje
        db.rollback()
        print("❌ ERROR EN CREAR_USUARIO (SQLAlchemy):", str(e.__dict__.get('orig')))
        return None
    except Exception as e:
        # Cualquier otro error
        db.rollback()
        print("❌ ERROR EN CREAR_USUARIO:", e)
        return None


def autenticar_usuario(db: Session, correo: str, contrasena: str):
    """
    Verifica correo/contraseña. Retorna el usuario ORM si es válido, o None.
    """
    try:
        user = db.query(models.Usuario).filter(models.Usuario.correo == correo.strip().lower()).first()
        if not user:
            print("⚠️ Usuario no encontrado:", correo)
            return None

        # Truncar contraseña recibida de la misma forma antes de verificar
        contrasena_bytes = contrasena.encode("utf-8")
        contrasena_truncada = contrasena_bytes[:72].decode("utf-8", "ignore")

        if not verify_password(contrasena_truncada, user.contrasena):
            print("⚠️ Contraseña incorrecta para:", correo)
            return None

        print(f"✅ Usuario autenticado correctamente: {correo}")
        return user

    except SQLAlchemyError as e:
        print("❌ ERROR EN AUTENTICAR_USUARIO (SQLAlchemy):", str(e.__dict__.get('orig')))
        return None
    except Exception as e:
        print("❌ ERROR EN AUTENTICAR_USUARIO:", e)
        return None
