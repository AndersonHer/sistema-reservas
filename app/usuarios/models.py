from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.settings import settings

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    rol = Column(Enum('usuario', 'admin'), default='usuario')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        