@echo off
title Iniciando API de Usuarios
echo ==============================================
echo  Iniciando servidor FastAPI de Usuarios...
echo ==============================================

REM Activar entorno virtual
call .venv\Scripts\activate

REM Ejecutar el servidor en el puerto 8001
start http://127.0.0.1:8001/docs
uvicorn app.usuarios.main:app --reload --port 8001

pause
