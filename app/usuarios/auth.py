# app/usuarios/auth.py
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.settings import settings
from . import models

# Seguridad / hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme (espera "Authorization: Bearer <token>")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")

# Funciones de hashing
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Función para crear JWT
def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=(expires_minutes if expires_minutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

# Función para decodificar/verificar JWT (lanza excepción si inválido/expirado)
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

# Dependencia para obtener usuario actual desde token (útil en rutas protegidas)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(models.get_db)):
    payload = decode_access_token(token)
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin 'sub'")
    user = db.query(models.Usuario).filter(models.Usuario.id == int(sub)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user
