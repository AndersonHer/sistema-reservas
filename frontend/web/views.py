# views.py - VERSIÓN COMPLETA CON INTEGRACIÓN DE MICROSERVICIOS
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string
from .models import Usuario, Recurso, Reserva, PasswordResetToken

# Configuración de microservicios
MICROSERVICES = {
    'usuarios': 'http://localhost:8000',      
    'recursos': 'http://localhost:8001',       
    'reservas': 'http://localhost:8002',      
    'disponibilidad': 'http://localhost:8004', 
    'reportes': 'http://localhost:8003'       
}
class MicroserviceClient:
    """Cliente para comunicarse con los microservicios"""
    
    def obtener_recursos(self):
        """Obtener recursos del microservicio de recursos"""
        try:
            response = requests.get(f"{MICROSERVICES['recursos']}/recursos/", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error obteniendo recursos: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error conectando al servicio de recursos: {e}")
            return []
    
    def crear_reserva(self, reserva_data):
        """Crear reserva a través del microservicio de reservas"""
        try:
            response = requests.post(
                f"{MICROSERVICES['reservas']}/reservas/", 
                json=reserva_data,
                timeout=5
            )
            if response.status_code == 200:
                return {'success': True, 'reserva': response.json()}
            else:
                return {'success': False, 'error': f'Error del servicio: {response.text}'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Error de conexión: {str(e)}'}
    
    def obtener_reservas_usuario(self, usuario_id):
        """Obtener reservas del usuario desde el microservicio"""
        try:
            response = requests.get(
                f"{MICROSERVICES['reservas']}/reservas/usuario/{usuario_id}/",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error obteniendo reservas: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error conectando al servicio de reservas: {e}")
            return []
    
    def verificar_disponibilidad(self, recurso_id, fecha, hora_inicio, hora_fin):
        """Verificar disponibilidad con el microservicio correspondiente"""
        try:
            params = {
                'recurso_id': recurso_id,
                'fecha': fecha,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin
            }
            response = requests.get(
                f"{MICROSERVICES['disponibilidad']}/disponibilidad/check/",
                params=params,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {'disponible': False, 'error': 'Error verificando disponibilidad'}
        except requests.exceptions.RequestException as e:
            return {'disponible': False, 'error': f'Error de conexión: {str(e)}'}
    
    def login_usuario(self, email, password):
        """Login a través del microservicio de usuarios"""
        try:
            response = requests.post(
                f"{MICROSERVICES['usuarios']}/usuarios/login",
                json={'email': email, 'password': password},
                timeout=5
            )
            if response.status_code == 200:
                return {'success': True, 'usuario': response.json()}
            else:
                return {'success': False, 'error': 'Credenciales incorrectas'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Error de conexión: {str(e)}'}
    
    def registrar_usuario(self, datos_usuario):
        """Registrar usuario a través del microservicio"""
        try:
            response = requests.post(
                f"{MICROSERVICES['usuarios']}/usuarios/registro",
                json=datos_usuario,
                timeout=5
            )
            if response.status_code == 200:
                return {'success': True, 'usuario': response.json()}
            else:
                return {'success': False, 'error': response.json().get('detail', 'Error en registro')}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Error de conexión: {str(e)}'}

def home(request):
    """Página de inicio - redirige al login o dashboard según sesión"""
    if request.session.get('user'):
        return redirect('dashboard')
    return redirect('login')

def password_reset_request(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            usuario = Usuario.objects.get(email=email, activo=True)
            
            # Generar token único
            token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(50))
            
            # Crear expiración (1 hora)
            expira_en = timezone.now() + timezone.timedelta(hours=1)
            
            # Guardar token en la base de datos
            reset_token = PasswordResetToken.objects.create(
                usuario=usuario,
                token=token,
                expira_en=expira_en
            )
            
            # Enviar email
            reset_url = f"http://127.0.0.1:8000/password-reset-confirm/{token}/"
            
            subject = 'Recuperación de Contraseña - Sistema de Reservas'
            message = f'''
            Hola {usuario.nombre},
            
            Has solicitado recuperar tu contraseña para el Sistema de Reservas.
            
            Para restablecer tu contraseña, haz clic en el siguiente enlace:
            {reset_url}
            
            Este enlace expirará en 1 hora.
            
            Si no solicitaste este cambio, ignora este mensaje.
            
            Saludos,
            Equipo del Sistema de Reservas
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                fail_silently=False,
            )
            
            print(f"URL de recuperación para {usuario.email}: {reset_url}")
            
            return render(request, 'web/password_reset_sent.html', {
                'email': usuario.email
            })
            
        except Usuario.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            return render(request, 'web/password_reset_sent.html', {
                'email': email
            })
    
    return render(request, 'web/password_reset_request.html')

def password_reset_confirm(request, token):
    """Vista para confirmar recuperación con token"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.es_valido():
            return render(request, 'web/password_reset_invalid.html')
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password != confirm_password:
                return render(request, 'web/password_reset_confirm.html', {
                    'token': token,
                    'error': 'Las contraseñas no coinciden'
                })
            
            if len(password) < 6:
                return render(request, 'web/password_reset_confirm.html', {
                    'token': token,
                    'error': 'La contraseña debe tener al menos 6 caracteres'
                })
            
            # Actualizar contraseña
            usuario = reset_token.usuario
            usuario.hashed_password = make_password(password)
            usuario.save()
            
            # Marcar token como usado
            reset_token.usado = True
            reset_token.save()
            
            subject = 'Contraseña Actualizada - Sistema de Reservas'
            message = f'''
            Hola {usuario.nombre},
            
            Tu contraseña ha sido actualizada exitosamente.
            
            Si no realizaste este cambio, por favor contacta al administrador inmediatamente.
            
            Saludos,
            Equipo del Sistema de Reservas
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                fail_silently=False,
            )
            
            return render(request, 'web/password_reset_complete.html')
        
        return render(request, 'web/password_reset_confirm.html', {
            'token': token
        })
        
    except PasswordResetToken.DoesNotExist:
        return render(request, 'web/password_reset_invalid.html')

def login_view(request):
    """Vista para login de usuarios"""
    # Si ya está logueado, redirigir al dashboard
    if request.session.get('user'):
        return redirect('dashboard')
    
    ms_client = MicroserviceClient()
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # TEMPORAL: Para probar, permitir login con cualquier contraseña para usuarios existentes
        try:
            usuario = Usuario.objects.get(email=email, activo=True)
            # Login exitoso (sin verificar contraseña por ahora - TEMPORAL)
            request.session['user'] = {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'rol': usuario.rol
            }
            return redirect('dashboard')
        except Usuario.DoesNotExist:
            # Si no existe, intentar con microservicio
            resultado = ms_client.login_usuario(email, password)
            if resultado['success']:
                usuario = resultado['usuario']
                request.session['user'] = {
                    'id': usuario['id'],
                    'nombre': usuario['nombre'],
                    'email': usuario['email'],
                    'rol': usuario['rol']
                }
                return redirect('dashboard')
            else:
                return render(request, 'web/login.html', {
                    'error': resultado['error']
                })
    
    return render(request, 'web/login.html')

def registro_view(request):
    """Vista para registro de nuevos usuarios"""
    # Si ya está logueado, redirigir al dashboard
    if request.session.get('user'):
        return redirect('dashboard')
    
    ms_client = MicroserviceClient()
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        rol = request.POST.get('rol', 'estudiante')
        
        # Validaciones
        if password != confirm_password:
            return render(request, 'web/registro.html', {
                'error': 'Las contraseñas no coinciden',
                'form_data': request.POST
            })
        
        if len(password) < 6:
            return render(request, 'web/registro.html', {
                'error': 'La contraseña debe tener al menos 6 caracteres',
                'form_data': request.POST
            })
        
        # Registrar en microservicio
        resultado = ms_client.registrar_usuario({
            'nombre': nombre,
            'email': email,
            'password': password
        })
        
        if resultado['success']:
            # Guardar en sesión y redirigir
            usuario = resultado['usuario']
            request.session['user'] = {
                'id': usuario['id'],
                'nombre': usuario['nombre'],
                'email': usuario['email'],
                'rol': usuario['rol']
            }
            return redirect('dashboard')
        else:
            # Fallback: registrar en base de datos local
            try:
                if Usuario.objects.filter(email=email).exists():
                    return render(request, 'web/registro.html', {
                        'error': 'Este email ya está registrado',
                        'form_data': request.POST
                    })
                
                usuario = Usuario(
                    nombre=nombre,
                    email=email,
                    hashed_password=make_password(password),
                    rol=rol,
                    activo=True
                )
                usuario.save()
                
                request.session['user'] = {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'rol': usuario.rol
                }
                return redirect('dashboard')
                
            except Exception as e:
                return render(request, 'web/registro.html', {
                    'error': f'Error al crear usuario: {str(e)}',
                    'form_data': request.POST
                })
    
    return render(request, 'web/registro.html')

def dashboard(request):
    """Vista principal del dashboard"""
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    # Usar microservicio para obtener recursos
    ms_client = MicroserviceClient()
    recursos_data = ms_client.obtener_recursos()
    
    # Obtener reservas del usuario actual usando microservicio
    reservas_data = ms_client.obtener_reservas_usuario(user['id'])
    
    # Si el microservicio falla, usar base de datos local como fallback
    if not recursos_data:
        recursos = Recurso.objects.all()
        recursos_data = [
            {
                'id': r.id,
                'nombre': r.nombre,
                'tipo': r.tipo,
                'descripcion': r.descripcion,
                'estado': r.estado
            }
            for r in recursos
        ]
    
    if not reservas_data:
        reservas_usuario = Reserva.objects.filter(usuario_id=user['id'])
        reservas_data = []
        for reserva in reservas_usuario:
            try:
                recurso = Recurso.objects.get(id=reserva.recurso_id)
                reservas_data.append({
                    'id': reserva.id,
                    'recurso_nombre': recurso.nombre,
                    'recurso_tipo': recurso.tipo,
                    'fecha': reserva.fecha,
                    'hora_inicio': reserva.hora_inicio,
                    'hora_fin': reserva.hora_fin,
                    'estado': reserva.estado
                })
            except Recurso.DoesNotExist:
                reservas_data.append({
                    'id': reserva.id,
                    'recurso_nombre': 'Recurso no encontrado',
                    'recurso_tipo': 'desconocido',
                    'fecha': reserva.fecha,
                    'hora_inicio': reserva.hora_inicio,
                    'hora_fin': reserva.hora_fin,
                    'estado': reserva.estado
                })
    
    context = {
        'user': user,
        'recursos': recursos_data,
        'reservas': reservas_data,
        'total_recursos': len(recursos_data),
        'total_reservas': len(reservas_data),
        'recursos_disponibles': len([r for r in recursos_data if r.get('estado') == 'disponible'])
    }
    return render(request, 'web/dashboard.html', context)

def recursos_view(request):
    """Vista para listar todos los recursos"""
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    # Usar microservicio para obtener recursos
    ms_client = MicroserviceClient()
    recursos_data = ms_client.obtener_recursos()
    
    # Fallback a base de datos local si el microservicio falla
    if not recursos_data:
        recursos = Recurso.objects.all()
        recursos_data = [
            {
                'id': r.id,
                'nombre': r.nombre,
                'tipo': r.tipo,
                'descripcion': r.descripcion,
                'estado': r.estado
            }
            for r in recursos
        ]
    
    return render(request, 'web/recursos.html', {
        'user': user,
        'recursos': recursos_data
    })

def reservas_view(request):
    """Vista para listar reservas del usuario"""
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    # Obtener reservas del usuario actual usando microservicio
    ms_client = MicroserviceClient()
    reservas_data = ms_client.obtener_reservas_usuario(user['id'])
    
    # Fallback a base de datos local si el microservicio falla
    if not reservas_data:
        reservas = Reserva.objects.filter(usuario_id=user['id'])
        reservas_data = []
        for reserva in reservas:
            try:
                recurso = Recurso.objects.get(id=reserva.recurso_id)
                reservas_data.append({
                    'id': reserva.id,
                    'recurso_nombre': recurso.nombre,
                    'recurso_tipo': recurso.tipo,
                    'fecha': reserva.fecha,
                    'hora_inicio': reserva.hora_inicio,
                    'hora_fin': reserva.hora_fin,
                    'estado': reserva.estado
                })
            except Recurso.DoesNotExist:
                reservas_data.append({
                    'id': reserva.id,
                    'recurso_nombre': 'Recurso no encontrado',
                    'recurso_tipo': 'desconocido',
                    'fecha': reserva.fecha,
                    'hora_inicio': reserva.hora_inicio,
                    'hora_fin': reserva.hora_fin,
                    'estado': reserva.estado
                })
    
    return render(request, 'web/reservas.html', {
        'user': user,
        'reservas': reservas_data
    })

def nueva_reserva_view(request):
    """Vista para crear nueva reserva"""
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    ms_client = MicroserviceClient()
    
    if request.method == 'POST':
        # Procesar nueva reserva
        recurso_id = request.POST.get('recurso_id')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        
        # Verificar disponibilidad primero
        disponibilidad = ms_client.verificar_disponibilidad(
            recurso_id, fecha, hora_inicio, hora_fin
        )
        
        if not disponibilidad.get('disponible', False):
            error_msg = disponibilidad.get('error', 'El recurso no está disponible en ese horario')
            
            # Obtener recursos para mostrar en el template
            recursos_data = ms_client.obtener_recursos()
            if not recursos_data:
                recursos = Recurso.objects.filter(estado='disponible')
                recursos_data = [
                    {
                        'id': r.id,
                        'nombre': r.nombre,
                        'tipo': r.tipo,
                        'descripcion': r.descripcion,
                        'estado': r.estado
                    }
                    for r in recursos
                ]
            
            return render(request, 'web/nueva_reserva.html', {
                'user': user,
                'recursos': recursos_data,
                'error': error_msg
            })
        
        # Crear reserva
        reserva_data = {
            'usuario_id': user['id'],
            'recurso_id': int(recurso_id),
            'fecha': fecha,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
            'estado': 'activa'
        }
        
        resultado = ms_client.crear_reserva(reserva_data)
        
        if resultado['success']:
            return redirect('reservas')
        else:
            # Obtener recursos para mostrar en el template
            recursos_data = ms_client.obtener_recursos()
            if not recursos_data:
                recursos = Recurso.objects.filter(estado='disponible')
                recursos_data = [
                    {
                        'id': r.id,
                        'nombre': r.nombre,
                        'tipo': r.tipo,
                        'descripcion': r.descripcion,
                        'estado': r.estado
                    }
                    for r in recursos
                ]
            
            return render(request, 'web/nueva_reserva.html', {
                'user': user,
                'recursos': recursos_data,
                'error': resultado['error']
            })
    
    # GET request - mostrar formulario
    recursos_data = ms_client.obtener_recursos()
    
    # Fallback a base de datos local si el microservicio falla
    if not recursos_data:
        recursos = Recurso.objects.filter(estado='disponible')
        recursos_data = [
            {
                'id': r.id,
                'nombre': r.nombre,
                'tipo': r.tipo,
                'descripcion': r.descripcion,
                'estado': r.estado
            }
            for r in recursos
        ]
    
    return render(request, 'web/nueva_reserva.html', {
        'user': user,
        'recursos': recursos_data
    })

def logout_view(request):
    """Vista para cerrar sesión"""
    request.session.flush()
    return redirect('home')