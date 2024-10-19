from django.db import models
from django.contrib.auth.models import User
from autenticacion.models import Profile
from datetime import timedelta, date
from django.utils import timezone
from autenticacion.models import Region, Provincia, Comuna  # Importamos los modelos de ubicación

class Terapeuta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    especialidad = models.CharField(max_length=100)
    fecha_ingreso = models.DateField(default=timezone.now)
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
    patologia = models.CharField(max_length=100, null=True, blank=True)
    descripcion_patologia = models.TextField(null=True, blank=True)
    medicamentos = models.CharField(max_length=500, null=True, blank=True)
    alergias = models.CharField(max_length=100, null=True, blank=True)
    motivo_desvinculacion = models.CharField(
        max_length=500,
        null=True, blank=True
    )
    actividad_fisica = models.CharField(
        max_length=100,
        choices=(
            ("Sedentario", "Sedentario"), 
            ("Moderado", "Moderado"), 
            ("Activo", "Activo")
        ),
        null=True, blank=True
    )
    
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.0)
    altura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.0)

    # Nuevas relaciones con Región, Provincia y Comuna
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.SET_NULL, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True)

    # Dirección detallada (Calle)
    calle = models.CharField(max_length=255, null=True, blank=True)

    # Fecha de creación del paciente
    date_joined = models.DateField(default=timezone.now)  
    
    # El paciente estará activo por defecto
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def calcular_imc(self, *args, **kwargs):
        """Calcula el imc en base al peso y altura ingresados en el forms.py"""
        if self.altura and self.altura > 0:  # Asegúrate de que la altura no sea cero
            imc = round(self.peso / (self.altura ** 2), 2)  # IMC = peso / altura^2
        else:
            imc = None
        
        return imc

    def calcular_edad(self):
        """ Calcula la edad actual del paciente basada en su fecha de nacimiento. """
        hoy = date.today()  # Fecha actual
        edad = hoy.year - self.fecha_nacimiento.year

        # Ajuste si la fecha de nacimiento aún no ha ocurrido este año
        if hoy.month < self.fecha_nacimiento.month or (hoy.month == self.fecha_nacimiento.month and hoy.day < self.fecha_nacimiento.day):
            edad -= 1

        return edad

class Cita(models.Model):
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE, null=True, blank=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True)
    titulo = models.CharField(max_length=50)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()
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
    angulo_min = models.IntegerField(null=True, blank=True)
    angulo_max = models.IntegerField(null=True, blank=True)
    velocidad = models.IntegerField(null=True, blank=True)
    repeticiones = models.IntegerField(null=True, blank=True)
    observaciones = models.CharField(max_length=500)
    estado = models.CharField(max_length=50, default="Pendiente", choices=(("Pendiente", "Pendiente"), ("Realizada", "Realizada")))

    def __str__(self):
        terapeuta_nombre = f"{self.rutina.terapeuta.user.first_name} {self.rutina.terapeuta.user.last_name}" if self.rutina and self.rutina.terapeuta else "Sin terapeuta"
        paciente_nombre = f"{self.rutina.paciente.user.first_name} {self.rutina.paciente.user.last_name}" if self.rutina and self.rutina.paciente else "Sin paciente"
        return f"{terapeuta_nombre} - {paciente_nombre}"
    
class Corriente(models.Model):
    sesion = models.ForeignKey(Sesion, related_name='corriente', on_delete=models.CASCADE, null=True, blank=True)
    corriente = models.FloatField()
    hora = models.DateTimeField(auto_now=True)

class Horario(models.Model):
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE, null=True, blank=True)
    dia = models.CharField(max_length=50, choices=(("Lunes", "Lunes"), ("Martes", "Martes"), ("Miércoles", "Miércoles"), ("Jueves", "Jueves"), ("Viernes", "Viernes"), ("Sábado", "Sábado"), ("Domingo", "Domingo")))
    hora_inicio = models.TimeField()
    hora_final = models.TimeField()

    def __str__(self):
        return f"{self.terapeuta.user.first_name} {self.terapeuta.user.last_name} - {self.dia}"
      
class Observacion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='observaciones')
    fecha = models.DateField(auto_now_add=True)
    contenido = models.TextField()

    def __str__(self):
        return f"{self.paciente.first_name} {self.paciente.last_name}"
