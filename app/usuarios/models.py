# app/usuarios/models.py
from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, create_engine
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Crear la base declarativa
Base = declarative_base()

# Configurar el motor y la sesión
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    rol = Column(Enum('usuario', 'admin'), default='usuario')
    creado_at = Column(TIMESTAMP, server_default=func.now())  # <-- agregado para coincidir con MySQL

# Dependencia para obtener conexión DB en cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
