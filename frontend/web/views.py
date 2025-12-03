import requests
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string
from .models import Usuario, Recurso, Reserva, PasswordResetToken

MICROSERVICES = {
    'usuarios': 'http://localhost:8000',      
    'recursos': 'http://localhost:8001',       
    'reservas': 'http://localhost:8002',      
    'disponibilidad': 'http://localhost:8004', 
    'reportes': 'http://localhost:8003'       
}

class MicroserviceClient:
    def __init__(self):
        self.session = requests.Session()

    def obtener_recursos(self):
        try:
            response = self.session.get(f"{MICROSERVICES['recursos']}/recursos/", timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []
    
    def crear_reserva(self, reserva_data):
        try:
            response = self.session.post(
                f"{MICROSERVICES['reservas']}/reservas/", 
                json=reserva_data,
                timeout=5
            )
            if response.status_code == 200:
                return {'success': True, 'reserva': response.json()}
            # Intentar leer el error del backend
            try:
                error_msg = response.json().get('detail', 'Error desconocido')
            except:
                error_msg = response.text
            return {'success': False, 'error': f'Error: {error_msg}'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Error de conexión: {str(e)}'}
    
    # --- NUEVOS MÉTODOS PARA GESTIÓN DE RESERVAS ---
    def cancelar_reserva(self, reserva_id):
        """Elimina una reserva (DELETE)"""
        try:
            response = self.session.delete(
                f"{MICROSERVICES['reservas']}/reservas/{reserva_id}",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def actualizar_reserva(self, reserva_id, datos):
        """Actualiza fecha/hora de una reserva (PUT)"""
        try:
            response = self.session.put(
                f"{MICROSERVICES['reservas']}/reservas/{reserva_id}",
                json=datos,
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    # -----------------------------------------------

    def obtener_reservas_usuario(self, usuario_id):
        try:
            response = self.session.get(
                f"{MICROSERVICES['reservas']}/reservas/usuario/{usuario_id}/",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []

    def obtener_todas_reservas(self):
        try:
            response = self.session.get(
                f"{MICROSERVICES['reservas']}/reservas/",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []
    
    def verificar_disponibilidad(self, recurso_id, fecha, hora_inicio, hora_fin):
        try:
            params = {
                'recurso_id': recurso_id,
                'fecha': fecha,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin
            }
            response = self.session.get(
                f"{MICROSERVICES['disponibilidad']}/disponibilidad/check/",
                params=params,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return {'disponible': False, 'error': 'Error verificando disponibilidad'}
        except requests.exceptions.RequestException as e:
            return {'disponible': False, 'error': f'Error de conexión: {str(e)}'}
    
    def login_usuario(self, email, password):
        try:
            response = self.session.post(
                f"{MICROSERVICES['usuarios']}/usuarios/login",
                json={'email': email, 'password': password},
                timeout=5
            )
            if response.status_code == 200:
                return {'success': True, 'usuario': response.json()}
            return {'success': False, 'error': 'Credenciales incorrectas'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Error de conexión: {str(e)}'}
    
    def registrar_usuario(self, datos_usuario):
        try:
            response = self.session.post(
                f"{MICROSERVICES['usuarios']}/usuarios/registro",
                json=datos_usuario,
                timeout=5
            )
            if response.status_code == 200:
                return {'success': True, 'usuario': response.json()}
            # Capturar detalle del error (ej. validación fallida)
            try:
                detail = response.json().get('detail')
                msg = str(detail) if detail else 'Error en el registro'
            except:
                msg = "Error desconocido en el servidor"
            return {'success': False, 'error': msg}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Error de conexión: {str(e)}'}

def home(request):
    """Página principal con Galería y Productos"""
    ms_client = MicroserviceClient()
    recursos_data = ms_client.obtener_recursos()
    
    if not recursos_data:
        recursos = Recurso.objects.all()
        recursos_data = [{'id': r.id, 'nombre': r.nombre, 'tipo': r.tipo, 'descripcion': r.descripcion} for r in recursos]
    
    return render(request, 'web/home.html', {
        'recursos': recursos_data,
        'user': request.session.get('user')
    })

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email, activo=True)
            token = ''.join(secrets.choice(string.digits) for _ in range(6))
            expira_en = timezone.now() + timezone.timedelta(minutes=15)
            
            PasswordResetToken.objects.create(
                usuario=usuario,
                token=token,
                expira_en=expira_en
            )
            
            subject = 'Código de Recuperación - Sistema de Reservas'
            message = f'''Hola {usuario.nombre},
            
            Tu código de verificación es: {token}
            
            Úsalo para restablecer tu contraseña. Este código expira en 15 minutos.
            '''
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [usuario.email], fail_silently=False)
            request.session['reset_email'] = usuario.email
            return redirect('password_reset_confirm')
            
        except Usuario.DoesNotExist:
            request.session['reset_email'] = email
            return redirect('password_reset_confirm')
    
    return render(request, 'web/password_reset_request.html')

def password_reset_confirm(request, token=None):
    email = request.session.get('reset_email')
    
    if not email:
        return redirect('password_reset_request')
        
    if request.method == 'POST':
        codigo_input = request.POST.get('token')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        
        if password != confirm:
            return render(request, 'web/password_reset_confirm.html', {'error': 'Las contraseñas no coinciden', 'email': email})
        
        try:
            usuario = Usuario.objects.get(email=email, activo=True)
            token_valido = PasswordResetToken.objects.filter(
                usuario=usuario,
                token=codigo_input,
                usado=False,
                expira_en__gt=timezone.now()
            ).last()
            
            if not token_valido:
                return render(request, 'web/password_reset_confirm.html', {'error': 'Código inválido o expirado', 'email': email})
            
            usuario.hashed_password = make_password(password)
            usuario.save()
            
            token_valido.usado = True
            token_valido.save()
            
            del request.session['reset_email']
            return render(request, 'web/password_reset_complete.html')
            
        except Usuario.DoesNotExist:
            return render(request, 'web/password_reset_confirm.html', {'error': 'Usuario no encontrado', 'email': email})
            
    return render(request, 'web/password_reset_confirm.html', {'email': email})

def login_view(request):
    if request.session.get('user'):
        return redirect('dashboard')
    
    ms_client = MicroserviceClient()
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            usuario = Usuario.objects.get(email=email, activo=True)
            if check_password(password, usuario.hashed_password):
                request.session['user'] = {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'rol': usuario.rol
                }
                return redirect('dashboard')
            else:
                return render(request, 'web/login.html', {'error': 'Credenciales incorrectas'})
                
        except Usuario.DoesNotExist:
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
                return render(request, 'web/login.html', {'error': resultado.get('error', 'Credenciales incorrectas')})
    
    return render(request, 'web/login.html')

def registro_view(request):
    if request.session.get('user'):
        return redirect('dashboard')
    
    ms_client = MicroserviceClient()
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono') # <-- CAPTURAMOS EL TELÉFONO
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        rol = request.POST.get('rol', 'estudiante')
        
        if password != confirm:
            return render(request, 'web/registro.html', {'error': 'Contraseñas no coinciden', 'form_data': request.POST})
        
        # Enviamos datos al microservicio
        datos_usuario = {
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'password': password
        }
        
        resultado = ms_client.registrar_usuario(datos_usuario)
        
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
            return render(request, 'web/registro.html', {'error': resultado['error'], 'form_data': request.POST})
    
    return render(request, 'web/registro.html')

def dashboard(request):
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    ms_client = MicroserviceClient()
    recursos_data = []
    reservas_data = []
    
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_recursos = executor.submit(ms_client.obtener_recursos)
            
            if user['rol'] == 'admin':
                future_reservas = executor.submit(ms_client.obtener_todas_reservas)
            else:
                future_reservas = executor.submit(ms_client.obtener_reservas_usuario, user['id'])
            
            recursos_data = future_recursos.result()
            reservas_data = future_reservas.result()
    except Exception:
        pass

    if not recursos_data:
        recursos = Recurso.objects.all()
        recursos_data = [{'id': r.id, 'nombre': r.nombre, 'tipo': r.tipo, 'estado': r.estado} for r in recursos]
    
    if not reservas_data:
        if user['rol'] == 'admin':
            reservas_local = Reserva.objects.all()
        else:
            reservas_local = Reserva.objects.filter(usuario_id=user['id'])
        reservas_data = [{'id': r.id, 'recurso_id': r.recurso_id, 'fecha': r.fecha, 'hora_inicio': r.hora_inicio, 'estado': r.estado} for r in reservas_local]

    recursos_map = {r['id']: r for r in recursos_data}
    reservas_enriquecidas = []

    for reserva in reservas_data:
        r_dict = reserva if isinstance(reserva, dict) else {
            'id': reserva.id, 
            'recurso_id': reserva.recurso_id,
            'fecha': reserva.fecha,
            'hora_inicio': reserva.hora_inicio,
            'hora_fin': reserva.hora_fin,
            'estado': reserva.estado
        }
        
        recurso = recursos_map.get(r_dict.get('recurso_id'))
        
        if recurso:
            r_dict['recurso_nombre'] = recurso['nombre']
            r_dict['recurso_tipo'] = recurso['tipo']
        else:
            r_dict['recurso_nombre'] = 'Recurso no encontrado'
            r_dict['recurso_tipo'] = 'desconocido'
            
        reservas_enriquecidas.append(r_dict)
    
    context = {
        'user': user,
        'recursos': recursos_data,
        'reservas': reservas_enriquecidas,
        'total_recursos': len(recursos_data),
        'total_reservas': len(reservas_enriquecidas),
        'recursos_disponibles': len([r for r in recursos_data if r.get('estado') == 'disponible'])
    }
    return render(request, 'web/dashboard.html', context)

def recursos_view(request):
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    ms_client = MicroserviceClient()
    recursos_data = ms_client.obtener_recursos()
    
    if not recursos_data:
        recursos = Recurso.objects.all()
        recursos_data = [{'id': r.id, 'nombre': r.nombre, 'tipo': r.tipo, 'estado': r.estado} for r in recursos]
    
    return render(request, 'web/recursos.html', {'user': user, 'recursos': recursos_data})

def reservas_view(request):
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    ms_client = MicroserviceClient()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_recursos = executor.submit(ms_client.obtener_recursos)
        future_reservas = executor.submit(ms_client.obtener_reservas_usuario, user['id'])
        recursos_data = future_recursos.result() or []
        reservas_data = future_reservas.result() or []
        
    recursos_map = {r['id']: r for r in recursos_data}
    reservas_enriquecidas = []
    
    for reserva in reservas_data:
        r_dict = reserva.copy() if isinstance(reserva, dict) else reserva.__dict__
        recurso = recursos_map.get(r_dict.get('recurso_id'))
        if recurso:
            r_dict['recurso_nombre'] = recurso['nombre']
            r_dict['recurso_tipo'] = recurso['tipo']
        else:
            r_dict['recurso_nombre'] = 'Desconocido'
            r_dict['recurso_tipo'] = '-'
        reservas_enriquecidas.append(r_dict)

    return render(request, 'web/reservas.html', {'user': user, 'reservas': reservas_enriquecidas})

def nueva_reserva_view(request):
    user = request.session.get('user')
    if not user:
        return redirect('login')
    
    ms_client = MicroserviceClient()
    
    if request.method == 'POST':
        recurso_id = request.POST.get('recurso_id')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        
        disponibilidad = ms_client.verificar_disponibilidad(recurso_id, fecha, hora_inicio, hora_fin)
        
        if not disponibilidad.get('disponible', False):
            recursos_data = ms_client.obtener_recursos()
            return render(request, 'web/nueva_reserva.html', {
                'user': user, 
                'recursos': recursos_data, 
                'error': disponibilidad.get('mensaje', 'Horario no disponible')
            })
        
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
            recursos_data = ms_client.obtener_recursos()
            return render(request, 'web/nueva_reserva.html', {
                'user': user, 
                'recursos': recursos_data, 
                'error': resultado['error']
            })
    
    recursos_data = ms_client.obtener_recursos()
    return render(request, 'web/nueva_reserva.html', {'user': user, 'recursos': recursos_data})

def logout_view(request):
    request.session.flush()
    return redirect('home')

# ================= NUEVAS VISTAS (ACCIONES) =================

def cancelar_reserva(request, reserva_id):
    """Acción para cancelar una reserva"""
    if not request.session.get('user'):
        return redirect('login')
        
    ms_client = MicroserviceClient()
    ms_client.cancelar_reserva(reserva_id)
    # Redirige de vuelta a la lista de reservas
    return redirect('reservas')

def posponer_reserva(request, reserva_id):
    """Acción para posponer (editar) una reserva"""
    user = request.session.get('user')
    if not user:
        return redirect('login')
        
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        
        ms_client = MicroserviceClient()
        
        datos_update = {
            "fecha": fecha,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin
        }
        
        # Intentamos actualizar. Si el backend valida conflicto, lanzará error.
        # Aquí simplificamos redirigiendo siempre, pero podrías manejar el error.
        ms_client.actualizar_reserva(reserva_id, datos_update)
            
    return redirect('reservas')