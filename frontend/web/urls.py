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
    path('logout/', views.logout_view, name='logout'),
    
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]