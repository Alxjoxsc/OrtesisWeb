from django import forms
from terapeuta.models import Terapeuta, Paciente
from autenticacion.models import Region, Provincia, Comuna  # Asegúrate de importar tus modelos
from django.utils import timezone  # Para manejar la fecha y hora actual

class CrearPacienteForm(forms.ModelForm):

    ACTIVIDAD_FISICA_CHOICES = [
        ('Sedentario', 'Sedentario'),
        ('Moderado', ' Moderado'),
        ('Activo', 'Activo'),
    ]

    rut = forms.CharField(
        max_length=12,
        label='Rut', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: XX.XXX.XXX-X'})
    )

    first_name = forms.CharField(
        max_length=150, 
        label='Nombres', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: Juan Alberto'})
    )

    last_name = forms.CharField(
        max_length=150, 
        label='Apellidos', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: Pérez González'})
    )

    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento', 
        required=True,
        widget=forms.DateInput(attrs={'class':'campo-formulario', 'type': 'date'})
    )

    sexo = forms.ChoiceField(
        choices=(('Masculino', 'Masculino'), ('Femenino', 'Femenino'), ("Otro", "Otro")), 
        label='Sexo', 
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    telefono = forms.CharField(
        max_length=12, 
        label='Teléfono', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: +56 9 1234 5678'})
    )

    email = forms.EmailField(
        label='Correo electrónico', 
        required=True,
        widget=forms.EmailInput(attrs={'class':'campo-formulario','placeholder': 'correodejemplo@ejemplos.com'})
    )

    contacto_emergencia = forms.CharField(
        max_length=150, 
        label='Contacto de emergencia', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: Juan Alberto Pérez Gonzales'})
    )

    telefono_emergencia = forms.CharField(
        max_length=12, 
        label='Teléfono', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: +56 9 1234 5678'})
    )

    historial_medico = forms.CharField(
        max_length=100, 
        label='Historial Médico', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario', 'placeholder' :'Ingrese el historial médico del paciente'})
    )

    medicamentos = forms.CharField(
        max_length=255, 
        label='Medicamentos', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario', 'placeholder' :'Ingrese los medicamentos que consume el paciente'})
    )

    patologia = forms.CharField(
        max_length=50, 
        label='Patología', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario', 'placeholder' :'Ingrese la patología del paciente'})
    )

    alergia = forms.CharField(
        max_length=255, 
        label='Alergias', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ingrese las alergias del Paciente'})
    )

    dispositivo_ortesis = forms.CharField(
        max_length=255, 
        label='Dispositivo Órtesis', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ingrese el dispositivo de órtesis a utilizar'})
    )

    actividad_fisica = forms.ChoiceField(
        choices=ACTIVIDAD_FISICA_CHOICES,
        label='Actividad Física',
        required=False,
        widget=forms.Select(attrs={'class':'campo-formulario'})
    )

    peso = forms.DecimalField(
        max_digits=5,  # Máximo 5 dígitos en total, incluyendo decimales
        decimal_places=2,  # 2 decimales
        label='Peso (kg)',
        required=False,
        widget=forms.NumberInput(attrs={'class':'campo-formulario', 'placeholder': 'Ej: 70.50'})
    )

    estatura = forms.DecimalField(
        max_digits=4,  # Máximo 4 dígitos en total (ej. 1.75 o 175.0)
        decimal_places=2,  # 2 decimales
        label='Estatura (m)',
        required=False,
        widget=forms.NumberInput(attrs={'class':'campo-formulario', 'placeholder': 'Ej: 1.75'})
    )

    direccion = forms.CharField(
        max_length=255, 
        label='Dirección', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: Calle 123, Comuna, Región'})
    )

    class Meta:
        model = Paciente
        fields = [
            'rut', 
            'first_name', 
            'last_name', 
            'fecha_nacimiento', 
            'sexo', 
            'telefono', 
            'email', 
            'contacto_emergencia', 
            'telefono_emergencia', 
            'historial_medico', 
            'medicamentos', 
            'patologia', 
            'alergia', 
            'dispositivo_ortesis', 
            'actividad_fisica', 
            'peso', 
            'estatura', 
            'direccion',  # Incluido como un campo adicional
        ]

    def save(self, commit=True):
        # Creamos el paciente con los datos del formulario
        paciente = Paciente.objects.create(
            rut=self.cleaned_data['rut'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
            sexo=self.cleaned_data['sexo'],
            telefono=self.cleaned_data['telefono'],
            email=self.cleaned_data['email'],
            contacto_emergencia=self.cleaned_data['contacto_emergencia'],
            telefono_emergencia=self.cleaned_data['telefono_emergencia'],
            historial_medico=self.cleaned_data['historial_medico'],
            medicamentos=self.cleaned_data['medicamentos'],
            patologia=self.cleaned_data['patologia'],
            alergias=self.cleaned_data['alergia'],  # Corregido
            dispositivo_ortesis=self.cleaned_data['dispositivo_ortesis'],
            actividad_fisica=self.cleaned_data['actividad_fisica'],
            peso=self.cleaned_data['peso'],
            altura=self.cleaned_data['estatura'],  # Corregido
            direccion=self.cleaned_data['direccion'],  # Nuevo
            progreso='',  # Campo predeterminado vacío
            motivo_desvinculacion='',  # Campo predeterminado vacío
            date_joined=timezone.now(),  # Fecha de creación asignada automáticamente
            is_active=True  # Activo por defecto
        )

        if commit:
            paciente.save()

        return paciente  # Retornamos el paciente creado
