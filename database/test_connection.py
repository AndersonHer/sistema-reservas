import pymysql
from config.settings import settings

def test_mysql_connection():
    """Probar conexión directa a MySQL con pymysql"""
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            port=int(settings.DB_PORT)
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        connection.close()
        print("✅ Conexión a MySQL exitosa")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Verifica:")
        print("   - MySQL está ejecutándose")
        print("   - Credenciales en .env son correctas")
        print("   - Base de datos 'sistema_reservas' existe")
        return False

if __name__ == "__main__":
    test_mysql_connection()