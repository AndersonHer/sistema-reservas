from pydantic import BaseModel, EmailStr, field_validator
import re
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str  # Nuevo campo
    password: str

    # Validación: Nombre solo letras y espacios
    @field_validator('nombre')
    def validar_nombre(cls, v):
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", v):
            raise ValueError('El nombre solo puede contener letras')
        return v

    # Validación: Teléfono solo números
    @field_validator('telefono')
    def validar_telefono(cls, v):
        if not v.isdigit():
            raise ValueError('El teléfono solo puede contener números')
        if len(v) < 8:
            raise ValueError('El teléfono debe tener al menos 8 dígitos')
        return v

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None # Nuevo campo
    rol: str
    activo: bool

    class Config:
        from_attributes = True