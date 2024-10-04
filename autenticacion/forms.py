import re
from itertools import cycle
from django import forms
from django.core.exceptions import ValidationError

class RutLoginForm(forms.Form):
    rut = forms.CharField(max_length=12, label="RUT")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    remember_me = forms.BooleanField(required=False, label="Recordarme")
    
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

        # Validación del dígito verificador
        if dv != verificador:
            raise forms.ValidationError('El dígito verificador del RUT no es válido.')
        return rut


#----------------------------Formulario de recuperar contrasena----------------------------
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico", max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Validar que el correo tenga un dominio correcto
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError("El correo electrónico no es válido. Asegúrate de que tenga un formato correcto, como example@domain.com")
        return email
    

class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        min_length=8,
        help_text="La contraseña debe tener al menos 8 caracteres, incluir un número, una letra, y un carácter especial (!@#$%^&*.,)."
    )
    confirm_password = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput,
        min_length=8
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetNewPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Validar que las contraseñas coincidan
        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden. Por favor, intenta de nuevo.")
        return cleaned_data

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        
        # Validar que la nueva contraseña no sea igual a la contraseña anterior
        if self.user.check_password(new_password):
            raise ValidationError("La nueva contraseña no puede ser igual a la contraseña anterior.")
        
        # Validar que la contraseña tenga al menos un carácter especial, un número y una letra
        password_regex = r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*.,]).{8,}$'
        if not re.match(password_regex, new_password):
            raise ValidationError("La contraseña debe contener al menos un carácter especial, un número y una letra.")
        
        return new_password