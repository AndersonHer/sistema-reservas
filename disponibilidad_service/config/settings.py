import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class Settings:
    # ----------------------------
    # Configuración base de la BD
    # ----------------------------
    def __init__(self):
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_NAME = os.getenv('DB_NAME', 'sistema_reservas')
        self.DB_USER = os.getenv('DB_USER', 'root')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'megadelicias123')  # valor por defecto

        # Construir URL de conexión después de cargar variables
        self.DATABASE_URL = os.getenv(
            'DATABASE_URL',
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"
        )

        # ----------------------------
        # Configuración JWT
        # ----------------------------
        self.JWT_SECRET = os.getenv('JWT_SECRET', 'clave-secreta-local')
        self.JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60))

        # Alias para compatibilidad con otros archivos
        self.SECRET_KEY = self.JWT_SECRET
        self.ALGORITHM = self.JWT_ALGORITHM

        # ----------------------------
        # Configuración AWS (solo producción)
        # ----------------------------
        self.AWS_CONFIG = {
            'region': os.getenv('AWS_REGION', 'us-east-1')
        }

# Instancia global de configuración
settings = Settings()
