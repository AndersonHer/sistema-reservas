import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # ----------------------------
    # Configuración base de la BD
    # ----------------------------
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'sistema_reservas')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # URL de conexión completa (para SQLAlchemy)
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )

    # ----------------------------
    # Configuración JWT
    # ----------------------------
    JWT_SECRET = os.getenv('JWT_SECRET', 'clave-secreta-local')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60))

    # Alias para compatibilidad con otros archivos
    SECRET_KEY = JWT_SECRET
    ALGORITHM = JWT_ALGORITHM

    # ----------------------------
    # Configuración AWS (solo producción)
    # ----------------------------
    AWS_CONFIG = {
        'region': os.getenv('AWS_REGION', 'us-east-1')
    }

settings = Settings()
