import subprocess
import time

services = [
    "uvicorn usuarios_service.main:app --reload --port 8000",
    "uvicorn recursos_service.main:app --reload --port 8001",
    "uvicorn reservas_service.main:app --reload --port 8002",
    "uvicorn reportes_service.main:app --reload --port 8003",
    "uvicorn disponibilidad_service.main:app --reload --port 8004",
]

print("🚀 Iniciando microservicios...")

# Ejecutar todos los servicios
for cmd in services:
    subprocess.Popen(cmd, shell=True)
    time.sleep(2)

print("✅ Servicios iniciados en puertos 8000-8004")
print("📝 Ve a http://localhost:8000/docs para probar")
print("🛑 Presiona ENTER para detener todos los servicios")

input()  # Esperar hasta que presiones ENTER

print("⏹️  Deteniendo servicios...")
subprocess.run("taskkill /f /im uvicorn.exe", shell=True)
print("✅ Todos detenidos")