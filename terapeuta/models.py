from django.db import models
from django.contrib.auth.models import User
from autenticacion.models import Profile
from datetime import timedelta
from django.utils import timezone

class Terapeuta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    especialidad = models.CharField(max_length=100)
    fecha_ingreso = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], default='Activo')
    disponibilidad = models.CharField(max_length=30, choices=[('Disponible', 'Disponible'), ('Medianamente Disponible', 'Medianamente Disponible'), ('No Disponible', 'No Disponible')], default='Disponible')
    horas_trabajadas = models.FloatField(default=0)
    fecha_contratacion = models.DateField()
    titulo = models.CharField(max_length=100, default="Sin título")
    experiencia = models.IntegerField(null=True, blank=True)
    presentacion = models.CharField(max_length=500, default="¡Hola! Soy tu terapeuta. Estoy aquí para ayudarte a mejorar tu calidad de vida. ¡Vamos a trabajar juntos!") 
    correo_contacto = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Paciente(models.Model):
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE, null=True, blank=True)
    rut = models.CharField(max_length=13)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10, choices=(("Masculino", "Masculino"), ("Femenino", "Femenino"), ("Otro", "Otro")))
    telefono = models.CharField(max_length=13, null=True, blank=True)
    email = models.CharField(max_length=254, null=True, blank=True)
    contacto_emergencia = models.CharField(max_length=100, null=True, blank=True)
    telefono_emergencia = models.CharField(max_length=12, null=True, blank=True)
    historial_medico = models.TextField(null=True, blank=True)
    medicamentos = models.CharField(max_length=500, null=True, blank=True)
    patologia = models.CharField(max_length=100, null=True, blank=True)
    alergias = models.CharField(max_length=100, null=True, blank=True)
    progreso = models.TextField(null=True, blank=True)
    dispositivo_ortesis = models.CharField(max_length=100, null=True, blank=True)
    actividad_fisica = models.CharField(max_length=100, choices=(("Sedentario", "Sedentario"), ("Moderado", "Moderado"), ("Activo", "Activo")), null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.0)
    altura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.0)
    imc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.0)
    motivo_desvinculacion = models.CharField(max_length=500, choices=(("Terminó tratamiento", "Terminó tratamiento"), ("Cambio de terapeuta", "Cambio de terapeuta"), ("Otro", "Otro")), null=True, blank=True)
    date_joined = models.DateField()
    direccion = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Cita(models.Model):
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE, null=True, blank=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True)
    titulo = models.CharField(max_length=50)
    fecha = models.DateField()
    hora = models.TimeField()
    sala = models.CharField(max_length=50)
    detalle = models.CharField(max_length=100)
    def __str__(self):
        terapeuta_nombre = f"{self.terapeuta.user.first_name} {self.terapeuta.user.last_name}" if self.terapeuta else "Sin terapeuta"
        paciente_nombre = f"{self.paciente.user.first_name} {self.paciente.user.last_name}" if self.paciente else "Sin paciente"
        return f"{terapeuta_nombre} - {paciente_nombre}"

class Rutina(models.Model):
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE, null=True, blank=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    estado = models.CharField(max_length=50, default="Pendiente", choices=(("Pendiente", "Pendiente"), ("Realizada", "Realizada"), ("Cancelada", "Cancelada")))
    angulo_inicial = models.IntegerField()
    angulo_final = models.IntegerField()
    repeticiones = models.IntegerField()
    velocidad = models.IntegerField()
    descripcion = models.CharField(max_length=500)

    def __str__(self):
        terapeuta_nombre = f"{self.terapeuta.user.first_name} {self.terapeuta.user.last_name}" if self.terapeuta else "Sin terapeuta"
        paciente_nombre = f"{self.paciente.user.first_name} {self.paciente.user.last_name}" if self.paciente else "Sin paciente"
        return f"{terapeuta_nombre} - {paciente_nombre}"

class Sesion(models.Model):
    rutina = models.ForeignKey(Rutina, related_name='sesiones', on_delete=models.CASCADE, null=True, blank=True)
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()
    fecha = models.DateField()
    duracion = models.IntegerField()
    corriente = models.DecimalField(max_digits=5, decimal_places=2)
    observaciones = models.CharField(max_length=500)

    def __str__(self):
        terapeuta_nombre = f"{self.rutina.terapeuta.user.first_name} {self.rutina.terapeuta.user.last_name}" if self.rutina and self.rutina.terapeuta else "Sin terapeuta"
        paciente_nombre = f"{self.rutina.paciente.user.first_name} {self.rutina.paciente.user.last_name}" if self.rutina and self.rutina.paciente else "Sin paciente"
        return f"{terapeuta_nombre} - {paciente_nombre}"

class Horario(models.Model):
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE, null=True, blank=True)
    dia = models.CharField(max_length=50, choices=(("Lunes", "Lunes"), ("Martes", "Martes"), ("Miércoles", "Miércoles"), ("Jueves", "Jueves"), ("Viernes", "Viernes"), ("Sábado", "Sábado"), ("Domingo", "Domingo")))
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()

    def __str__(self):
        return f"{self.terapeuta.user.first_name} {self.terapeuta.user.last_name} - {self.dia}"
