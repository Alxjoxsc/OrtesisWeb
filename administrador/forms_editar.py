from itertools import cycle
from django import forms
from django.contrib.auth.models import User, Group
from autenticacion.models import Profile
from terapeuta.models import Terapeuta, Horario
from autenticacion.models import Region, Provincia, Comuna  # Asegúrate de importar tus modelos
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.core.mail import send_mail # Importar la función send_mail, para enviar correos electrónicos
from django.utils.crypto import get_random_string # Importar la función get_random_string, para generar una contraseña aleatoria
import re
from datetime import date
from django.conf import settings
from terapeuta.models import Paciente
from decimal import Decimal
def is_valid_email(text):
        pattern = r'^[a-z][a-z0-9\-\.]+@[a-z]+\.[a-z]{1,3}$'

        return re.search(pattern, text)

class CrearTerapeutaForm(forms.ModelForm):
    # Campo del modelo 'Profile'

    rut = forms.CharField(
        max_length=12,
        label='Rut', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: XX.XXX.XXX-X'})
    )

    # Campos del modelo 'User'

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
    email = forms.EmailField(
        label='Correo electrónico', 
        required=True,
        widget=forms.EmailInput(attrs={'class':'campo-formulario','placeholder': 'correodejemplo@ejemplos.com'})
    )

    # Campos del modelo 'Profile'

    telefono = forms.CharField(
        max_length=11, 
        label='Teléfono', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: 9 1234 5678'})
    )
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento', 
        required=True,
        widget=forms.DateInput(attrs={'class':'campo-formulario', 'type': 'date'})
    )
    direccion = forms.CharField(
        max_length=255, 
        label='Dirección', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: Calle Ejemplo 123'})
    )
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(), 
        label='Región', 
        required=True,
        widget=forms.Select(attrs={'class':'campo-formulario'})
    )
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.none(), 
        label='Provincia', 
        required=True,
        widget=forms.Select(attrs={'class':'campo-formulario'})
    )
    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.none(), 
        label='Comuna', 
        required=True,
        widget=forms.Select(attrs={'class':'campo-formulario'})
    )
    sexo = forms.ChoiceField(
        choices=(('M', 'Masculino'), ('F', 'Femenino')), 
        label='Sexo', 
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    # Campos del modelo 'Terapeuta'

    especialidad = forms.CharField(
        max_length=100, 
        label='Especialidad', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario', 'placeholder' :'Ej: Articulaciones Superiores'})
    )
    fecha_contratacion = forms.DateField(
        label='Fecha de contratación', 
        required=True,
        widget=forms.DateInput(attrs={'class':'campo-formulario', 'type': 'date'})
    )
    titulo = forms.CharField(
        max_length=100, 
        label='Título', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario', 'placeholder': 'Ej: Licenciado en Terapia Ocupacional'})
    )
    experiencia = forms.IntegerField(
        label='Experiencia', 
        required=True,
        widget=forms.NumberInput(attrs={'class':'campo-formulario'})
    )
    presentacion = forms.CharField(
        max_length=500, 
        label='Presentación', 
        required=False,
        widget=forms.Textarea(attrs={'class':'campo-formulario','rows': 3})
    )
    correo_contacto = forms.EmailField(
        label='Correo de contacto', 
        required=False,
        widget=forms.EmailInput(attrs={'class':'campo-formulario','placeholder': 'correoejemplo@ejemplos.com'})
    )

    class Meta:
        model = Terapeuta
        fields = [
            'rut',
            'first_name',
            'last_name',
            'email',
            'telefono',
            'fecha_nacimiento',
            'direccion',
            'region',
            'provincia',
            'comuna',
            'sexo',
            'especialidad',
            'fecha_contratacion',
            'titulo',
            'experiencia',
            'presentacion',
            'correo_contacto'
        ]

    def save(self, commit=True):
        # Generar una contraseña aleatoria
        password = get_random_string(length=12)

        # Creamos el usuario primero
        user = User.objects.create_user(
            username=self.cleaned_data['rut'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=password  # Usamos la contraseña generada
        )
        if commit:
            user.save()
            
        # Agregar el usuario al grupo 'Terapeuta'
        grupo_terapeuta, created = Group.objects.get_or_create(name='Terapeuta')
        user.groups.add(grupo_terapeuta)  # Añadimos el usuario al grupo
        
        # Creamos el perfil del usuario
        profile = Profile.objects.create(
            user=user,
            rut=self.cleaned_data['rut'],
            telefono=self.cleaned_data['telefono'],
            fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
            direccion=self.cleaned_data['direccion'],
            region=self.cleaned_data['region'],  # Ahora es una instancia de Region
            provincia=self.cleaned_data['provincia'],  # Ahora es una instancia de Provincia
            comuna=self.cleaned_data['comuna'],  # Ahora es una instancia de Comuna
            sexo=self.cleaned_data['sexo']
        )
        if commit:
            profile.save()
        
        # Creamos el terapeuta
        terapeuta = Terapeuta.objects.create(
            user=user,
            especialidad=self.cleaned_data['especialidad'],
            fecha_contratacion=self.cleaned_data['fecha_contratacion'],
            titulo=self.cleaned_data['titulo'],
            experiencia=self.cleaned_data['experiencia'],
            presentacion=self.cleaned_data['presentacion'],
            correo_contacto=self.cleaned_data['correo_contacto']
        )
        if commit:
            terapeuta.save()
        
        # Enviar la contraseña por correo electrónico
        send_mail(
        'Bienvenido/a a la plataforma',
        f'Estimado/a {self.cleaned_data["first_name"]}, su cuenta ha sido creada.\n'
        f'Usuario: {self.cleaned_data["rut"]}\nContraseña: {password}\n'
        'Le recomendamos cambiar su contraseña al ingresar a la plataforma.',
        settings.DEFAULT_FROM_EMAIL,  # Usamos el emisor definido
        [self.cleaned_data['email']],  # Destinatario
        fail_silently=False,
        )

        return terapeuta  # Retornamos el terapeuta creado
    
    def __init__(self, *args, **kwargs):
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
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')

        # Validación del formato
        if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut):
            raise forms.ValidationError('El RUT debe estar en el formato XX.XXX.XXX-X.')

        # Se remueve el punto y el guión
        clean_rut = rut.replace(".", "").replace("-", "")

        # Se extrae la parte numérica y se verifica el dígito
        num_part = clean_rut[:-1]
        dv = clean_rut[-1].upper()

        # Validación del dígito verificador
        reversed_digits = map(int, reversed(num_part))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        verificador = (-s) % 11
        verificador = 'K' if verificador == 10 else str(verificador)
        print("Dígito verificador del formulario:", dv)
        print("Dígito verificador calculado:", verificador)

        # Validación del dígito verificador
        if dv != verificador:
            raise forms.ValidationError('El dígito verificador del RUT no es válido.')

        # Verificar si ya existe otro usuario con este RUT, excluyendo al usuario que estamos editando
        if Profile.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un usuario con este RUT.')

        return rut
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        # Permitir hasta 3 nombres separados por espacios
        if not re.match(r'^[a-zA-Z]+( [a-zA-Z]+){0,2}$', first_name):
            raise forms.ValidationError('El nombre solo puede contener letras y hasta 3 nombres separados por espacios.')
        
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        # Permitir hasta 2 apellidos separados por un espacio
        if not re.match(r'^[a-zA-Z]+( [a-zA-Z]+)?$', last_name):
            raise forms.ValidationError('El apellido solo puede contener letras y hasta 2 apellidos separados por un espacio.')
        
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not is_valid_email(email):
            raise forms.ValidationError('Por favor, ingrese una dirección de correo electrónico válida.')

        # Verificar si ya existe otro User con este email, excluyendo al User que estamos editando
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')

        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        # Validar el formato del teléfono con una expresión regular
        if not re.match(r'^\d{1} \d{4} \d{4}$', telefono):
            raise forms.ValidationError('El formato del teléfono debe ser: 9 1234 5678')
        
        return telefono
    
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        # Verificar que la fecha de nacimiento sea anterior a la fecha actual
        if fecha_nacimiento >= date.today():
            raise forms.ValidationError('La fecha de nacimiento debe ser anterior a la fecha actual.')
        
        return fecha_nacimiento
    
    def clean_direccion(self):
        direccion = self.cleaned_data['direccion']
        if not re.match(r'^[a-zA-Z\sáéíóúÁÉÍÓÚ]+ \d+$', direccion):
            raise forms.ValidationError('La dirección debe seguir el formato "Nombre de la calle número". Por ejemplo, "Los Alamos 999".')
        
        return direccion
    
    def clean_especialidad(self):
        especialidad = self.cleaned_data['especialidad']
        if not re.match(r'^[a-zA-Z\sáéíóúÁÉÍÓÚ]+$', especialidad):
            raise forms.ValidationError('La especialidad solo puede contener letras y espacios.')
        
        return especialidad
    
    def clean_fecha_contratacion(self):
        fecha_contratacion = self.cleaned_data['fecha_contratacion']
        # Verificar que la fecha de contratación sea anterior a la fecha actual
        if fecha_contratacion >= date.today():
            raise forms.ValidationError('La fecha de contratación debe ser anterior a la fecha actual.')
        
        return fecha_contratacion
    
    def clean_titulo(self):
        titulo = self.cleaned_data['titulo']
        if not re.match(r'^[a-zA-Z\sáéíóúÁÉÍÓÚ]+$', titulo):
            raise forms.ValidationError('El título solo puede contener letras y espacios.')
        
        return titulo
    
    def clean_experiencia(self):
        experiencia = self.cleaned_data['experiencia']
        # Verificar que la experiencia sea un número positivo
        if experiencia <= 0:
            raise forms.ValidationError('La experiencia debe ser un número positivo o igual a 0.')
        
        return experiencia
    
    def clean_presentacion(self):
        presentacion = self.cleaned_data.get('presentacion')
        if not re.match(r'^[a-zA-Z0-9\sáéíóúÁÉÍÓÚ.,;:¡!¿?()"\']+$', presentacion):
            raise forms.ValidationError('La presentación solo puede contener letras, números y signos de puntuación.')
        
        return presentacion
    
    def clean_correo_contacto(self):
        correo_contacto = self.cleaned_data.get('correo_contacto')
        if correo_contacto and not is_valid_email(correo_contacto):
            raise forms.ValidationError('Por favor, ingrese una dirección de correo electrónico válida para el contacto.')

        return correo_contacto
    


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['dia', 'hora_inicio', 'hora_final']
        widgets = {
            'dia': forms.Select(attrs={'class':'seleccion'}),
            'hora_inicio': forms.TimeInput(attrs={'class':'campo-formulario', 'type': 'time'}),
            'hora_final': forms.TimeInput(attrs={'class':'campo-formulario', 'type': 'time'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_final = cleaned_data.get('hora_final')

        # Verificar que la hora de inicio sea anterior a la hora final
        if hora_inicio and hora_final and hora_inicio >= hora_final:
            raise ValidationError('La hora de inicio debe ser anterior a la hora final.')

        return cleaned_data

# Creamos el formset para los horarios del terapeuta (inlineformset)
HorarioFormSet = inlineformset_factory(
    Terapeuta,
    Horario,
    form=HorarioForm,
    extra=1,  # Se envia solo un formularo. pero se pueden agregar más
    can_delete=True # Se pueden eliminar los formularios
)


class EditarPacienteForm(forms.ModelForm):

    ACTIVIDAD_FISICA_CHOICES = [
        ('Sedentario', 'Sedentario'),
        ('Moderado', ' Moderado'),
        ('Activo', 'Activo'),
    ]

    rut = forms.CharField(
        max_length=12,
        label='Rut (*)', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': Paciente.rut})
    )

    first_name = forms.CharField(
        max_length=150, 
        label='Nombres (*)', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: Juan Alberto'})
    )

    last_name = forms.CharField(
        max_length=150, 
        label='Apellidos (*)', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: Pérez González'})
    )

    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento (*)', 
        required=True,
        widget=forms.DateInput(attrs={'class':'campo-formulario', 'type': 'date'})
    )

    sexo = forms.ChoiceField(
        choices=(('Masculino', 'Masculino'), ('Femenino', 'Femenino'), ("Otro", "Otro")), 
        label='Sexo (*)', 
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    telefono = forms.CharField(
        max_length=12, 
        label='Teléfono (*)', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: 9 1234 5678'})
    )

    email = forms.EmailField(
        label='Correo electrónico (*)', 
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
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: 9 1234 5678'})
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
        label='Patología (*)', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario', 'placeholder' :'Ingrese la patología del paciente'})
    )

    alergias = forms.CharField(
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

    altura = forms.DecimalField(
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
        label='Provincia (*)',
        required=True,
        widget=forms.Select(attrs={'class': 'campo-formulario'})
    )

    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.all(),  # Cargamos todas las comunas
        label='Comuna (*)',
        required=True,
        widget=forms.Select(attrs={'class': 'campo-formulario'})
    )

    calle = forms.CharField(
        max_length=255,
        label='Calle (*)',
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
            'alergias', 
            'dispositivo_ortesis', 
            'actividad_fisica', 
            'peso', 
            'altura', 
            'region',  
            'provincia',  
            'comuna',  
            'calle',  
        ]

    def save(self, commit=True):
        paciente = super().save(commit=False)  # Obtén una instancia del paciente sin guardar
        # Aquí puedes hacer otras modificaciones a la instancia si es necesario
        if commit:
            paciente.save()  # Guarda la instancia en la base de datos
        return paciente
    
    def __init__(self, *args, **kwargs):
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
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')

        # Validación del formato
        if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut):
            raise forms.ValidationError('El RUT debe estar en el formato XX.XXX.XXX-X.')

        # Se remueve el punto y el guión
        clean_rut = rut.replace(".", "").replace("-", "")

        # Se extrae la parte numérica y se verifica el dígito
        num_part = clean_rut[:-1]
        dv = clean_rut[-1].upper()
                # Se extrae la parte numérica y se verifica el dígito
        num_part = clean_rut[:-1]
        dv = clean_rut[-1].upper()

        # Validación del dígito verificador
        reversed_digits = map(int, reversed(num_part))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        verificador = (-s) % 11
        verificador = 'K' if verificador == 10 else str(verificador)
        print("Dígito verificador del formulario:", dv)
        print("Dígito verificador calculado:", verificador)

        # Validación del dígito verificador
        if dv != verificador:
            raise forms.ValidationError('El dígito verificador del RUT no es válido.')

        # Verificar si ya existe otro usuario con este RUT, excluyendo al usuario que estamos editando
        if Profile.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un usuario con este RUT.')

        return rut
    
    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        print(f'Peso original: {peso}')
        if peso is not None:
            return Decimal(str(peso).replace(',', '.'))
        return peso

    def clean_altura(self):
        altura = self.cleaned_data.get('altura')
        print(f'Estatura original: {altura}')
        if altura is not None:
            return Decimal(str(altura).replace(',', '.'))
        return altura
    
        
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        # Permitir hasta 3 nombres separados por espacios
        if not re.match(r'^[a-zA-Z]+( [a-zA-Z]+){0,2}$', first_name):
            raise forms.ValidationError('El nombre solo puede contener letras y hasta 3 nombres separados por espacios.')
        
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        # Permitir hasta 2 apellidos separados por un espacio
        if not re.match(r'^[a-zA-Z]+( [a-zA-Z]+)?$', last_name):
            raise forms.ValidationError('El apellido solo puede contener letras y hasta 2 apellidos separados por un espacio.')
        
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not is_valid_email(email):
            raise forms.ValidationError('Por favor, ingrese una dirección de correo electrónico válida.')

        # Verificar si ya existe otro User con este email, excluyendo al User que estamos editando
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')

        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        # Validar el formato del teléfono con una expresión regular
        if not re.match(r'^\d{1} \d{4} \d{4}$', telefono):
            raise forms.ValidationError('El formato del teléfono debe ser: 9 1234 5678')
        
        return telefono
    
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        # Verificar que la fecha de nacimiento sea anterior a la fecha actual
        if fecha_nacimiento >= date.today():
            raise forms.ValidationError('La fecha de nacimiento debe ser anterior a la fecha actual.')
        
        return fecha_nacimiento

