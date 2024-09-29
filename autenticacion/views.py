from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .forms import RutLoginForm, SetPasswordForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from .forms import SendMailForm, SetPasswordForm
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.views import View
from .forms import RutLoginForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str  # Cambiado de force_text a force_str para Django 3.x+


# AUTENTICACION DE USUARIOS #

def login_usuario(request):
    # Verificar si el usuario ya está autenticado
    if request.user.is_authenticated:
        grupos = request.user.groups.all()
        
        if grupos.count() == 1:  # Si el usuario pertenece a un solo grupo
            return redireccionamiento_segun_rol(request.user, grupos.first())
        elif grupos.count() > 1:  # Si pertenece a múltiples grupos, mostrar opciones
            return redirect('elegir_rol')
        
    if request.method == 'POST':
        form = RutLoginForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            user = authenticate(request, rut=rut, password=password)
            
            if user is not None:
                # Usuario autenticado correctamente
                login(request, user)

                # Configuración de la duración de la sesión
                if remember_me is True:
                    request.session.set_expiry(1209600)  # Duración de 14 días
                else:
                    request.session.set_expiry(0)  # Expira al cerrar el navegador

                # Verificar roles del usuario a través de grupos
                grupos = user.groups.all()
                
                if grupos.count() == 1:  # Si el usuario pertenece a un solo grupo
                    return redireccionamiento_segun_rol(user, grupos.first())
                elif grupos.count() > 1:  # Si pertenece a múltiples grupos, mostrar opciones
                    return render(request, 'elegir_rol.html', {'roles': grupos})
            else:
                # Las credenciales son incorrectas o la cuenta está desactivada
                user = User.objects.filter(profile__rut=rut).first() # Buscar usuario por RUT
                if user and not user.is_active: # Si el usuario existe y está desactivado
                    # Usuario está desactivado
                    return render(request, 'login.html', {'form': form, 'error': 'Su cuenta está desactivada. Contacte al administrador.'})
                else:
                    # Credenciales incorrectas
                    return render(request, 'login.html', {'form': form, 'error': 'Credenciales incorrectas'})
    else:
        form = RutLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def elegir_rol(request):
    grupos = request.user.groups.all()
    if not grupos.exists():
        return redirect('acceso_denegado')  # Si el usuario no tiene roles, redirigir a acceso denegado
    
    if 'role' in request.GET:
        role_name = request.GET['role']
        try:
            group = Group.objects.get(name=role_name)
            if group in grupos:
                return redireccionamiento_segun_rol(request.user, group)
        except Group.DoesNotExist:
            return redirect('acceso_denegado')  # Si el grupo no existe, redirigir a acceso denegado

    return render(request, 'elegir_rol.html', {'roles': grupos})

def redireccionamiento_segun_rol(user, role):
    """Redirige según el rol"""
    if role.name == 'Administrador':
        return redirect('gestion_terapeutas')
    elif role.name == 'Terapeuta':
        return redirect('agenda')
    elif role.name == 'Recepcionista':
        return redirect('recepcionista_pacientes_activos')
    return redirect('login')  # Redirige en caso de no encontrar un rol

def logout_usuario(request):
    logout(request)
    return redirect('login')

def acceso_denegado(request):
    return render(request, 'acceso_denegado.html', {'message': 'No tienes permisos para acceder a esta página'})

# VISTAS DE RECUPERACIÓN DE CONTRASEÑA #

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

    def dispatch(self, *args, **kwargs):
        # Validar si el token es válido o si ya fue utilizado
        try:
            uid = force_str(urlsafe_base64_decode(self.kwargs['uidb64']))
            user = User.objects.get(pk=uid)
            if not default_token_generator.check_token(user, self.kwargs['token']):
                # Redirigir a acceso_denegado si el token es inválido o ya fue utilizado
                return redirect('acceso_denegado')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # Redirigir a acceso_denegado si algo sale mal (por ejemplo, usuario no encontrado)
            return redirect('acceso_denegado')

        # Si el token es válido, continuar con la vista normal
        return super().dispatch(*args, **kwargs)

class SendMailConfirmView(View):
    def get(self, request):
        form = SendMailForm()
        return render(request, 'password_reset_form.html', {'form': form})

    def post(self, request):
        form = SendMailForm(request.POST)
        if form.is_valid():
            # Lógica para enviar el correo
            # ...
            return render(request, 'password_reset_done.html')
        return render(request, 'password_reset_form.html', {'form': form})
