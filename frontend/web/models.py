from django.db import models

# Modelo para la tabla 'usuarios' existente
class Usuario(models.Model):
    ROLES = (
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('administrativo', 'Administrativo'),
        ('invitado', 'Invitado Externo'),  
        ('admin', 'Administrador'),
    )
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    hashed_password = models.CharField(max_length=255)
    
    # ÚNICA definición correcta de rol (max_length=50)
    rol = models.CharField(max_length=50, choices=ROLES, default='estudiante')
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuarios'
        managed = False

    def __str__(self):
        return f"{self.nombre} ({self.email})"

# Modelo para tokens de recuperación de contraseña
class PasswordResetToken(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    token = models.CharField(max_length=10) 
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_tokens'
    
    def __str__(self):
        return f"Token para {self.usuario.email}"
    
    def es_valido(self):
        from django.utils import timezone
        return not self.usado and timezone.now() < self.expira_en

# Modelo para la tabla 'recursos' existente
class Recurso(models.Model):
    TIPOS = (
        ('sala', 'Sala'),
        ('auditorio', 'Auditorio'),
        ('laboratorio', 'Laboratorio'),
        ('equipo', 'Equipo'),
    )
    
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('no disponible', 'No Disponible'),
    )
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=TIPOS)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')
    
    class Meta:
        db_table = 'recursos'
        managed = False

    def __str__(self):
        return self.nombre

# Modelo para la tabla 'reservas' existente
class Reserva(models.Model):
    ESTADOS = (
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
    )
    
    id = models.AutoField(primary_key=True)
    usuario_id = models.IntegerField()
    recurso_id = models.IntegerField()
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activa')
    
    class Meta:
        db_table = 'reservas'
        managed = False

    def __str__(self):
        return f"Reserva {self.id} - Usuario {self.usuario_id}"

# Modelo para la tabla 'usuarios_temp'
class UsuarioTemp(models.Model):
    ROLES = (
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('administrativo', 'Personal Administrativo'),
        ('admin', 'Administrador'),
    )
    
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    rol = models.CharField(max_length=50, choices=ROLES, default='estudiante') # También ajustado a 50 por seguridad
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuarios_temp'
        managed = False
    
    def __str__(self):
        return f"{self.nombre} ({self.email})"