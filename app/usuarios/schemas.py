# app/usuarios/schemas.py
from pydantic import BaseModel, EmailStr

class UsuarioCrear(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str

class UsuarioIniciarSesion(BaseModel):
    correo: EmailStr
    contrasena: str

class UsuarioSalida(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: str

    # Compatible con Pydantic v2 (reemplaza orm_mode)
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
