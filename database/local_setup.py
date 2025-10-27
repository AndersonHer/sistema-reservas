from sqlalchemy import create_engine
from config.settings import settings

def test_connection():
    """Probar conexión a la base de datos"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            print("✅ Conexión a MySQL exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def get_db_connection():
    """Obtener conexión a la base de datos"""
    engine = create_engine(settings.DATABASE_URL)
    return engine.connect()

if __name__ == "__main__":
    test_connection()