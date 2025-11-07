from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, time  
# Tus esquemas existentes...
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: bool

    class Config:
        from_attributes = True  # <-- CAMBIAR orm_mode por from_attributes

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ====================================================
#  ESQUEMAS NUEVOS PARA REPORTES (TU PARTE)
# ====================================================

class UsuarioInfo(BaseModel):
    id: int
    nombre: str

class RecursoInfo(BaseModel):
    id: int
    nombre: str
    tipo: Optional[str] = None

class HistorialItem(BaseModel):
    id: int
    reserva_id: int
    fecha_reserva: date
    hora_inicio: time
    hora_fin: time
    accion: str
    usuario: UsuarioInfo
    recurso: RecursoInfo

class HistorialResponse(BaseModel):
    total_registros: int
    historial: List[HistorialItem]

class ReporteUsuarioResponse(BaseModel):
    usuario: UsuarioInfo
    total_reservas: int
    historial: List[HistorialItem]

class ReporteRecursoResponse(BaseModel):
    recurso: RecursoInfo
    total_uso: int
    historial: List[HistorialItem]

class EstadisticasGenerales(BaseModel):
    total_usuarios: int
    total_recursos: int
    total_reservas: int
    reservas_activas: int
    reservas_canceladas: int

class EstadisticasHistorial(BaseModel):
    total_acciones: int
    reservas_unicas: int
    usuarios_activos: int

class EstadisticasResponse(BaseModel):
    estadisticas_generales: EstadisticasGenerales
    estadisticas_historial: EstadisticasHistorial