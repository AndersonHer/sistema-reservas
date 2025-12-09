from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recursos/', views.recursos_view, name='recursos'),
    path('reservas/', views.reservas_view, name='reservas'),
    path('reservas/nueva/', views.nueva_reserva_view, name='nueva_reserva'),
    
   
    path('reservas/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas/posponer/<int:reserva_id>/', views.posponer_reserva, name='posponer_reserva'),
    

    path('logout/', views.logout_view, name='logout'),
    
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reservas/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas/posponer/<int:reserva_id>/', views.posponer_reserva, name='posponer_reserva'),
]
# ... (imports y otras vistas) ...

def cancelar_reserva(request, reserva_id):
    if not request.session.get('user'):
        return redirect('login')
        
    ms_client = MicroserviceClient()
    # Llamamos al método DELETE del microservicio
    ms_client.cancelar_reserva(reserva_id) 
    return redirect('reservas')

def posponer_reserva(request, reserva_id):
    if not request.session.get('user'):
        return redirect('login')
        
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        
        ms_client = MicroserviceClient()
        datos = {
            "fecha": fecha,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin
        }
        # Llamamos al método PUT del microservicio
        ms_client.actualizar_reserva(reserva_id, datos)
            
    return redirect('reservas')