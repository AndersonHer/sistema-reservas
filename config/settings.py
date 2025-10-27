import os
from dotenv import load_dotenv

load_dotenv()

# Configuración base común
class Settings:
    # Database - Se sobrescribe localmente
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'sistema_reservas')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'clave-secreta-local')
    JWT_ALGORITHM = "HS256"
    
    # AWS (solo para producción)
    AWS_CONFIG = {
        'region': os.getenv('AWS_REGION', 'us-east-1')
    }

settings = Settings()