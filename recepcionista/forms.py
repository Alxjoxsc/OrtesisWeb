from django import forms
from terapeuta.models import Paciente
from autenticacion.models import Region, Provincia, Comuna  # Importamos los modelos de ubicación
from django.utils import timezone  # Para manejar la fecha y hora actual
from decimal import Decimal

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
        label='Teléfono Emergencia', 
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
        required=True,
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

    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),  # Cargamos todas las regiones
        label='Región',
        required=True,
        widget=forms.Select(attrs={'class': 'campo-formulario'})
    )

    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.all(),  # Cargamos todas las provincias
        label='Provincia',
        required=True,
        widget=forms.Select(attrs={'class': 'campo-formulario'})
    )

    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.all(),  # Cargamos todas las comunas
        label='Comuna',
        required=True,
        widget=forms.Select(attrs={'class': 'campo-formulario'})
    )

    calle = forms.CharField(
        max_length=255,
        label='Calle',
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: Calle 123'})
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
            'region',  # Añadido campo región
            'provincia',  # Añadido campo provincia
            'comuna',  # Añadido campo comuna
            'calle',  # Añadido campo calle
        ]

    def clean(self):
        cleaned_data = super().clean()

        # Validación ejemplo: Teléfono
        telefono = cleaned_data.get('telefono')
        if telefono and not telefono.startswith('+'):
            self.add_error('telefono', 'El número de teléfono debe comenzar con un "+" seguido del código de país.')

        # Validación para el campo de peso
        peso = cleaned_data.get('peso')
        if peso and peso <= 0:
            self.add_error('peso', 'El peso debe ser un valor positivo.')

        return cleaned_data
    
    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        print(f'Peso original: {peso}')
        if peso is not None:
            return Decimal(str(peso).replace(',', '.'))
        return peso

    def clean_estatura(self):
        estatura = self.cleaned_data.get('estatura')
        print(f'Estatura original: {estatura}')
        if estatura is not None:
            return Decimal(str(estatura).replace(',', '.'))
        return estatura

    def save(self, commit=True):
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
            alergias=self.cleaned_data['alergia'],
            dispositivo_ortesis=self.cleaned_data['dispositivo_ortesis'],
            actividad_fisica=self.cleaned_data['actividad_fisica'],
            peso=self.cleaned_data['peso'],
            altura=self.cleaned_data['estatura'],
            region=self.cleaned_data['region'],
            provincia=self.cleaned_data['provincia'],
            comuna=self.cleaned_data['comuna'],
            calle=self.cleaned_data['calle'],  # Calle agregada manualmente
            progreso='',
            motivo_desvinculacion='',
            date_joined=timezone.now(),
            is_active=True
        )

        if commit:
            paciente.save()

        return paciente
