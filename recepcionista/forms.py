from django import forms
from terapeuta.models import Paciente
from autenticacion.models import Region, Comuna  # Importamos los modelos de ubicación
from django.utils import timezone  # Para manejar la fecha y hora actual
from decimal import Decimal
from itertools import cycle
import re
from datetime import date

def is_valid_email(text):
        pattern = r'^[a-z][a-z0-9\-\.]+@[a-z]+\.[a-z]{1,3}$'

        return re.search(pattern, text)

class CrearPacienteForm(forms.ModelForm):

    ACTIVIDAD_FISICA_CHOICES = [
        ('Sedentario', 'Sedentario'),
        ('Moderado', ' Moderado'),
        ('Activo', 'Activo'),
    ]

    rut = forms.CharField(
        max_length=12,
        label='Rut (*)', 
        required=True,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: XX.XXX.XXX-X'})
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
    
    descripcion_patologia = forms.CharField(
        label='Descripción de la Patología (*)',
        max_length=1000,  # Limita la longitud del texto a 1000 caracteres
        required=True,  # Campo obligatorio
        widget=forms.Textarea(  # Se usa el widget Textarea
            attrs={
                'class': 'campo-formulario',  # Clase CSS personalizada
                'placeholder': 'Ingrese una descripción de la patología del paciente',  # Texto de marcador
                'rows': 5,  # Opcional: Número de líneas visibles en el textarea
                'cols': 50,  # Opcional: Número de caracteres visibles por línea
            }
        )
    )

    alergias = forms.CharField(
        max_length=255, 
        label='Alergias', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ingrese las alergias del Paciente'})
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
            'medicamentos', 
            'patologia', 
            'descripcion_patologia',
            'alergias', 
            'actividad_fisica', 
            'peso', 
            'altura', 
            'region',  # Añadido campo región
            'comuna',  # Añadido campo comuna
            'calle',  # Añadido campo calle
        ]

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
            medicamentos=self.cleaned_data['medicamentos'],
            patologia=self.cleaned_data['patologia'],
            descripcion_patologia=self.cleaned_data['descripcion_patologia'],
            alergias=self.cleaned_data['alergias'],
            actividad_fisica=self.cleaned_data['actividad_fisica'],
            peso=self.cleaned_data['peso'],
            altura=self.cleaned_data['altura'],
            region=self.cleaned_data['region'],
            comuna=self.cleaned_data['comuna'],
            calle=self.cleaned_data['calle'],  # Calle agregada manualmente
            motivo_desvinculacion='',
            date_joined=timezone.now(),
            is_active=True
        )

        if commit:
            paciente.save()

        return paciente
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar las comunas según la región seleccionada
        if 'region' in self.data:
            try:
                self.fields['comuna'].queryset = Comuna.objects.filter(region_id=self.data['region'])
            except (ValueError, TypeError):
                pass  # Manejo de errores si la región no es válida
        elif self.instance.pk:
            # Si ya existe la instancia, cargar las comunas de la región asociada
            self.fields['comuna'].queryset = self.instance.region.comuna_set.all()

    
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
        if Paciente.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
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
        # Permitir cualquier cantidad de nombres separados por espacios, solo letras y acentos
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ ]+$', first_name):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        # Permitir cualquier cantidad de apellidos separados por espacios, solo letras y acentos
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ ]+$', last_name):
            raise forms.ValidationError('El apellido solo puede contener letras y espacios.')
        
        return last_name

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not is_valid_email(email):
            raise forms.ValidationError('Por favor, ingrese una dirección de correo electrónico válida.')

        # Verificar si ya existe otro User con este email, excluyendo al User que estamos editando
        if Paciente.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
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
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ej: XX.XXX.XXX-X'})
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
    
    descripcion_patologia = forms.CharField(
        label='Descripción de la Patología (*)',
        max_length=1000,  # Limita la longitud del texto a 1000 caracteres
        required=True,  # Campo obligatorio
        widget=forms.Textarea(  # Se usa el widget Textarea
            attrs={
                'class': 'campo-formulario',  # Clase CSS personalizada
                'placeholder': 'Ingrese una descripción de la patología del paciente',  # Texto de marcador
                'rows': 5,  # Opcional: Número de líneas visibles en el textarea
                'cols': 50,  # Opcional: Número de caracteres visibles por línea
            }
        )
    )

    alergias = forms.CharField(
        max_length=255, 
        label='Alergias', 
        required=False,
        widget=forms.TextInput(attrs={'class':'campo-formulario','placeholder': 'Ingrese las alergias del Paciente'})
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
            'sexo', 
            'telefono', 
            'email', 
            'contacto_emergencia', 
            'telefono_emergencia', 
            'descripcion_patologia',
            'medicamentos', 
            'patologia', 
            'alergias', 
            'actividad_fisica', 
            'peso', 
            'altura', 
            'region',  
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
        
        # Filtrar las comunas según la región seleccionada
        if 'region' in self.data:
            try:
                self.fields['comuna'].queryset = Comuna.objects.filter(region_id=self.data['region'])
            except (ValueError, TypeError):
                pass  # Manejo de errores si la región no es válida
        elif self.instance.pk:
            # Si ya existe la instancia, cargar las comunas de la región asociada
            self.fields['comuna'].queryset = self.instance.region.comuna_set.all()

            
    def clean_peso(self):
        peso = self.cleaned_data.get('peso')
        print(f'Peso original: {peso}')
        if peso is not None:
            # Convertir la entrada a decimal y reemplazar comas por puntos si es necesario
            peso = Decimal(str(peso).replace(',', '.'))
            # Verificar que el peso no sea negativo ni mayor a 700 kg
            if peso < 0:
                raise forms.ValidationError('El peso no puede ser negativo.')
            if peso > 700:
                raise forms.ValidationError('El peso no puede ser mayor a 700 kg.')
        return peso

    def clean_altura(self):
        altura = self.cleaned_data.get('altura')
        # Verificar si se ingresó una altura
        if altura is not None:
            # Convertir la altura a string para aplicar la expresión regular
            altura_str = str(altura)
            # Expresión regular para validar el formato: 1 (parte entera) . 2 (dígitos decimales)
            if not re.match(r'^\d+(\.|\,)\d{1,2}$', altura_str):
                raise forms.ValidationError('El formato de la altura debe ser: 1.00 o 1,00 (máximo 2 decimales)')
            # Convertir a decimal para hacer la validación de rango
            altura = Decimal(str(altura_str).replace(',', '.'))
            # Validar que la altura esté en el rango permitido
            if altura < 0 or altura > 3:
                raise forms.ValidationError('La altura debe estar entre 0 y 3 metros.')
        return altura
        
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        # Permitir cualquier cantidad de nombres separados por espacios, solo letras y acentos
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ ]+$', first_name):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        # Permitir cualquier cantidad de apellidos separados por espacios, solo letras y acentos
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ ]+$', last_name):
            raise forms.ValidationError('El apellido solo puede contener letras y espacios.')
        
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not is_valid_email(email):
            raise forms.ValidationError('Por favor, ingrese una dirección de correo electrónico válida.')

        # Verificar si ya existe otro User con este email, excluyendo al User que estamos editando
        if Paciente.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un paciente con este correo electrónico.')

        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        # Validar el formato del teléfono con una expresión regular
        if not re.match(r'^\d{1} \d{4} \d{4}$', telefono):
            raise forms.ValidationError('El formato del teléfono debe ser: 9 1234 5678')
        
        return telefono
    
    def clean_alergias(self):
        alergias = self.cleaned_data.get('alergias')
        # Permitir múltiples palabras con letras, acentos, espacios y la letra ñ
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$', alergias):
            raise forms.ValidationError('Las alergias solo pueden contener letras (incluyendo acentos y espacios)')
        
        return alergias  
    
    def clean_contacto_emergencia(self):
        contacto_emergencia = self.cleaned_data.get('contacto_emergencia')
        # Permitir letras, acentos, espacios y la letra ñ para nombres
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', contacto_emergencia):
            raise forms.ValidationError('El contacto de emergencia solo puede contener letras (incluyendo acentos y espacios)')
        
        return contacto_emergencia
    
    def clean_patologia(self):
        patologia = self.cleaned_data.get('patologia')
        # Permitir letras, acentos, espacios y la letra ñ
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', patologia):
            raise forms.ValidationError('La patología solo puede contener letras (incluyendo acentos y espacios)')
        
        return patologia
    
    def clean_medicamentos(self):
        medicamentos = self.cleaned_data.get('medicamentos')
        # Permitir letras, acentos, espacios, la letra ñ y números
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]+$', medicamentos):
            raise forms.ValidationError('Los medicamentos no permiten caracteres especiales')
        
        return medicamentos
    
    def clean_historial_medico(self):
        historial_medico = self.cleaned_data.get('historial_medico')
        # Permitir letras, acentos, espacios, la letra ñ y números
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]+$', historial_medico):
            raise forms.ValidationError('El historial médico no permite caracteres especiales')
        
        return historial_medico
    
    def clean_calle(self):
        calle = self.cleaned_data.get('calle')
        # Permitir letras, tildes, ñ mayúsculas, espacios, números, puntos, # y -
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s.#\-]+$', calle):
            raise forms.ValidationError('La dirección no permite caracteres especiales, solo se permiten letras, números, espacios, puntos, # y -.')

        return calle
