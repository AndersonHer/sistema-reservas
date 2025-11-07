from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any
from datetime import date, time, timedelta

# Importar esquemas
from . import schemas

# Configuración de la base de datos
DATABASE_URL = "mysql+pymysql://root:Ujcv2025.16@localhost/sistema_reservas"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función auxiliar para convertir timedelta a time
def timedelta_to_time(td):
    """Convierte timedelta a time"""
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return time(hours, minutes, seconds)
    return td

# Crear la aplicación FastAPI
app = FastAPI(
    title="API de Reportes",
    version="1.0",
    description="""
    API para generar reportes del sistema de reservas
    
    Esta API permite:
    - Obtener historial completo de reservas
    - Generar reportes por usuario específico
    - Generar reportes por recurso específico  
    - Consultar estadísticas generales del sistema
    """
)

# Dependencia de base de datos
def get_db():
    """Crea y cierra una sesión de base de datos para cada petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ====================================================
# ENDPOINTS DE REPORTES
# ====================================================

@app.get("/reportes/historial", response_model=schemas.HistorialResponse, tags=["Reportes"])
def obtener_historial_completo(db: Session = Depends(get_db)):
    """
    Obtener el historial completo de reservas con información de usuarios y recursos
    """
    query = text("""
        SELECT 
            hr.id,
            hr.reserva_id,
            hr.fecha_reserva,
            hr.hora_inicio,
            hr.hora_fin,
            hr.accion,
            u.nombre as usuario_nombre,
            u.id as usuario_id,
            r.nombre as recurso_nombre,
            r.id as recurso_id,
            r.tipo as recurso_tipo
        FROM historial_reservas hr
        JOIN usuarios u ON hr.usuario_id = u.id
        JOIN recursos r ON hr.recurso_id = r.id
        ORDER BY hr.fecha_reserva DESC, hr.hora_inicio DESC
    """)
    
    result = db.execute(query)
    historial = []
    for row in result:
        historial.append({
            "id": row.id,
            "reserva_id": row.reserva_id,
            "fecha_reserva": row.fecha_reserva,
            "hora_inicio": timedelta_to_time(row.hora_inicio),
            "hora_fin": timedelta_to_time(row.hora_fin),
            "accion": row.accion,
            "usuario": {
                "id": row.usuario_id,
                "nombre": row.usuario_nombre
            },
            "recurso": {
                "id": row.recurso_id,
                "nombre": row.recurso_nombre,
                "tipo": row.recurso_tipo
            }
        })
    
    return {
        "total_registros": len(historial),
        "historial": historial
    }

@app.get("/reportes/usuario/{usuario_id}", response_model=schemas.ReporteUsuarioResponse, tags=["Reportes"])
def obtener_reportes_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obtener reportes específicos de un usuario
    """
    # Verificar si el usuario existe
    user_query = text("SELECT id, nombre FROM usuarios WHERE id = :usuario_id")
    user_result = db.execute(user_query, {"usuario_id": usuario_id})
    user = user_result.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener historial del usuario
    query = text("""
        SELECT 
            hr.id,
            hr.reserva_id,
            hr.fecha_reserva,
            hr.hora_inicio,
            hr.hora_fin,
            hr.accion,
            r.nombre as recurso_nombre,
            r.tipo as recurso_tipo,
            r.id as recurso_id
        FROM historial_reservas hr
        JOIN recursos r ON hr.recurso_id = r.id
        WHERE hr.usuario_id = :usuario_id
        ORDER BY hr.fecha_reserva DESC, hr.hora_inicio DESC
    """)
    
    result = db.execute(query, {"usuario_id": usuario_id})
    historial_usuario = []
    for row in result:
        historial_usuario.append({
            "id": row.id,
            "reserva_id": row.reserva_id,
            "fecha_reserva": row.fecha_reserva,
            "hora_inicio": timedelta_to_time(row.hora_inicio),
            "hora_fin": timedelta_to_time(row.hora_fin),
            "accion": row.accion,
            "usuario": {
                "id": user.id,
                "nombre": user.nombre
            },
            "recurso": {
                "id": row.recurso_id,
                "nombre": row.recurso_nombre,
                "tipo": row.recurso_tipo
            }
        })
    
    return {
        "usuario": {
            "id": user.id,
            "nombre": user.nombre
        },
        "total_reservas": len(historial_usuario),
        "historial": historial_usuario
    }

@app.get("/reportes/recurso/{recurso_id}", response_model=schemas.ReporteRecursoResponse, tags=["Reportes"])
def obtener_reportes_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """
    Obtener reportes específicos de un recurso
    """
    # Verificar si el recurso existe
    recurso_query = text("SELECT id, nombre, tipo FROM recursos WHERE id = :recurso_id")
    recurso_result = db.execute(recurso_query, {"recurso_id": recurso_id})
    recurso = recurso_result.fetchone()
    
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    
    # Obtener historial del recurso
    query = text("""
        SELECT 
            hr.id,
            hr.reserva_id,
            hr.fecha_reserva,
            hr.hora_inicio,
            hr.hora_fin,
            hr.accion,
            u.nombre as usuario_nombre,
            u.id as usuario_id
        FROM historial_reservas hr
        JOIN usuarios u ON hr.usuario_id = u.id
        WHERE hr.recurso_id = :recurso_id
        ORDER BY hr.fecha_reserva DESC, hr.hora_inicio DESC
    """)
    
    result = db.execute(query, {"recurso_id": recurso_id})
    historial_recurso = []
    for row in result:
        historial_recurso.append({
            "id": row.id,
            "reserva_id": row.reserva_id,
            "fecha_reserva": row.fecha_reserva,
            "hora_inicio": timedelta_to_time(row.hora_inicio),
            "hora_fin": timedelta_to_time(row.hora_fin),
            "accion": row.accion,
            "usuario": {
                "id": row.usuario_id,
                "nombre": row.usuario_nombre
            },
            "recurso": {
                "id": recurso.id,
                "nombre": recurso.nombre,
                "tipo": recurso.tipo
            }
        })
    
    return {
        "recurso": {
            "id": recurso.id,
            "nombre": recurso.nombre,
            "tipo": recurso.tipo
        },
        "total_uso": len(historial_recurso),
        "historial": historial_recurso
    }

@app.get("/reportes/estadisticas", response_model=schemas.EstadisticasResponse, tags=["Reportes"])
def obtener_estadisticas_generales(db: Session = Depends(get_db)):
    """
    Obtener estadísticas generales del sistema
    """
    # Estadísticas de usuarios
    usuarios_query = text("SELECT COUNT(*) as total FROM usuarios")
    usuarios_result = db.execute(usuarios_query)
    total_usuarios = usuarios_result.fetchone().total
    
    # Estadísticas de recursos
    recursos_query = text("SELECT COUNT(*) as total FROM recursos")
    recursos_result = db.execute(recursos_query)
    total_recursos = recursos_result.fetchone().total
    
    # Estadísticas de reservas
    reservas_query = text("""
        SELECT 
            COUNT(*) as total_reservas,
            SUM(CASE WHEN estado = 'activa' THEN 1 ELSE 0 END) as activas,
            SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) as canceladas
        FROM reservas
    """)
    reservas_result = db.execute(reservas_query)
    reservas_stats = reservas_result.fetchone()
    
    # Estadísticas del historial
    historial_query = text("""
        SELECT 
            COUNT(*) as total_acciones,
            COUNT(DISTINCT reserva_id) as reservas_unicas,
            COUNT(DISTINCT usuario_id) as usuarios_activos
        FROM historial_reservas
    """)
    historial_result = db.execute(historial_query)
    historial_stats = historial_result.fetchone()
    
    return {
        "estadisticas_generales": {
            "total_usuarios": total_usuarios,
            "total_recursos": total_recursos,
            "total_reservas": reservas_stats.total_reservas,
            "reservas_activas": reservas_stats.activas,
            "reservas_canceladas": reservas_stats.canceladas
        },
        "estadisticas_historial": {
            "total_acciones": historial_stats.total_acciones,
            "reservas_unicas": historial_stats.reservas_unicas,
            "usuarios_activos": historial_stats.usuarios_activos
        }
    }

# Endpoint de verificación de salud
@app.get("/")
def read_root():
    return {"message": "API de Reportes funcionando correctamente"}

# Endpoint para verificar conexión a BD
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Intentar ejecutar una consulta simple
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}