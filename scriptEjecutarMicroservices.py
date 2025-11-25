import subprocess
import time
import sys
import os
import signal

def check_service(port):
    """Verificar si un servicio está respondiendo"""
    try:
        import requests
        response = requests.get(f"http://localhost:{port}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    services = [
        {
            "name": "👥 Usuarios Service",
            "cmd": "uvicorn usuarios_service.main:app --reload --port 8000",
            "port": 8000,
            "url": "http://localhost:8000"
        },
        {
            "name": "🏢 Recursos Service", 
            "cmd": "uvicorn recursos_service.main:app --reload --port 8001",
            "port": 8001,
            "url": "http://localhost:8001"
        },
        {
            "name": "📅 Reservas Service",
            "cmd": "uvicorn reservas_service.main:app --reload --port 8002", 
            "port": 8002,
            "url": "http://localhost:8002"
        },
        {
            "name": "📊 Reportes Service",
            "cmd": "uvicorn reportes_service.main:app --reload --port 8003",
            "port": 8003,
            "url": "http://localhost:8003"
        },
        {
            "name": "✅ Disponibilidad Service",
            "cmd": "uvicorn disponibilidad_service.main:app --reload --port 8004",
            "port": 8004,
            "url": "http://localhost:8004"
        }
    ]

    processes = []
    
    print("🚀 SISTEMA DE RESERVAS - INICIANDO MICROSERVICIOS")
    print("=" * 60)

    # Ejecutar todos los servicios
    for service in services:
        print(f"▶️  Iniciando {service['name']}...", end=" ")
        
        try:
            process = subprocess.Popen(service["cmd"], shell=True)
            processes.append(process)
            time.sleep(3)  # Dar tiempo para que inicie
            
            # Verificar si el servicio está listo
            if check_service(service["port"]):
                print(f"✅ (Puerto {service['port']})")
            else:
                print(f"🟡 Iniciando... (Puerto {service['port']})")
                
        except Exception as e:
            print(f"❌ Error: {e}")

    print("=" * 60)
    print("✅ Microservicios iniciados:")
    
    for service in services:
        status = "✅ Activo" if check_service(service["port"]) else "🟡 Iniciando"
        print(f"   {service['name']}: {service['url']} - {status}")

    print(f"\n🎯 **NEXT STEP**: En otra terminal ejecuta:")
    print(f"   cd frontend && python manage.py runserver 8005")
    print(f"\n📱 Frontend estará en: http://localhost:8005")
    print(f"\n⏹️  Presiona CTRL+C para detener todos los servicios")

    # Función para limpiar procesos al salir
    def cleanup():
        print(f"\n🛑 Deteniendo servicios...")
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        # Asegurar que uvicorn se cierre
        subprocess.run("taskkill /f /im uvicorn.exe 2>nul", shell=True)
        subprocess.run("taskkill /f /im python.exe 2>nul", shell=True)
        print("✅ Todos los servicios detenidos")

    # Manejar CTRL+C
    try:
        # Mantener el script corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()