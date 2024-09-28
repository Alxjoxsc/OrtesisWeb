from django import forms
#from django.contrib.auth.models import User, Group
#from autenticacion.models import Profile
from terapeuta.models import Terapeuta, Paciente
from autenticacion.models import Region, Provincia, Comuna  # Asegúrate de importar tus modelos
from django.forms import inlineformset_factory

class CrearPacienteForm(forms.ModelForm):
    
    ACTIVIDAD_FISICA_CHOICES = [
        ('sedentario', 'Sedentario'),
        ('medianamente_activo', 'Medianamente Activo'),
        ('activo', 'Activo'),
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
        choices=(('M', 'Masculino'), ('F', 'Femenino')), 
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
    
    class Meta:
        model = Paciente  # Reemplaza 'Paciente' con el nombre de tu modelo
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
        ]
    

def save(self, commit=True):
    # Creamos el paciente
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
        alergia=self.cleaned_data['alergia'],
        dispositivo_ortesis=self.cleaned_data['dispositivo_ortesis'],
        actividad_fisica=self.cleaned_data['actividad_fisica'],
        peso=self.cleaned_data['peso'],
        estatura=self.cleaned_data['estatura'],
        especialidad=self.cleaned_data['especialidad'],
        fecha_contratacion=self.cleaned_data['fecha_contratacion'],
        titulo=self.cleaned_data['titulo'],
        experiencia=self.cleaned_data['experiencia'],
        presentacion=self.cleaned_data['presentacion'],
        correo_contacto=self.cleaned_data['correo_contacto'],
    )
    
    if commit:
        paciente.save()
    
    return paciente  # Retornamos el paciente creado

    
    '''def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'region' in self.data:
            try:
                self.fields['provincia'].queryset = Provincia.objects.filter(region_id=self.data['region'])
            except (ValueError, TypeError):
                pass  # Manejo de errores si la región no es válida
        elif self.instance.pk:
            self.fields['provincia'].queryset = self.instance.region.provincia_set.all()

        if 'provincia' in self.data:
            try:
                self.fields['comuna'].queryset = Comuna.objects.filter(provincia_id=self.data['provincia'])
            except (ValueError, TypeError):
                pass  # Manejo de errores si la provincia no es válida
        elif self.instance.pk:
            self.fields['comuna'].queryset = self.instance.provincia.comuna_set.all()
'''