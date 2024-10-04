from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Region(models.Model):
    nombre = models.CharField(max_length=255)
    
    def __str__(self):
        return self.nombre

class Provincia(models.Model):
    nombre = models.CharField(max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    nombre = models.CharField(max_length=255)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)  # RUT del usuario
    telefono = models.CharField(max_length=12, blank=True, null=True)  # Teléfono de contacto
    fecha_nacimiento = models.DateField(blank=True, null=True)  # Fecha de nacimiento
    direccion = models.CharField(max_length=255, blank=True, null=True)  # Dirección
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)  # Región
    provincia = models.ForeignKey(Provincia, on_delete=models.SET_NULL, null=True)  # Provincia
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True)  # Comuna
    sexo = models.CharField(max_length=1, choices=(('M', 'Masculino'), ('F', 'Femenino')), blank=True, null=True)  # Sexo
    
    def __str__(self):
        return f'{self.user.username} ({self.rut})'
    
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() <= self.created_at + timedelta(minutes=15)  # Token válido por 1 hora

    def __str__(self):
        return f'Token para {self.user.username}'
