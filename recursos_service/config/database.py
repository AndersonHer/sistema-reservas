from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings

# Crear motor de conexión
engine = create_engine(settings.DATABASE_URL)

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM
Base = declarative_base()

# Dependencia de sesión (para usar en rutas)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
