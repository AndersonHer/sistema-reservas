from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    telefono = Column(String(20), nullable=True)  # <-- Nuevo campo
    hashed_password = Column(String(255), nullable=False)
    rol = Column(String(50), default="estudiante")  
    activo = Column(Boolean, default=True)