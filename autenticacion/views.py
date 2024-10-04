import uuid
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import RutLoginForm, PasswordResetForm, SetNewPasswordForm
from .models import PasswordResetToken


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

##--------------------------------------------RECUPERAR CONTRASENA--------------------------------------------##
# views.py


# Solicitud de restablecimiento de contraseña
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generar un token único
                token = str(uuid.uuid4())
                # Crear y guardar el token en la base de datos
                PasswordResetToken.objects.create(user=user, token=token)

                # Construir la URL de restablecimiento de contraseña
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'token': token})
                )

                send_mail(
                    'Restablecimiento de contraseña',
                    f'Ha recibido este correo electrónico porque ha solicitado restablecer su contraseña en "OrtesisWeb".\n'
                    f'Por favor, dirijase al siguiente enlace para reestablecer su contraseña: {reset_url}\n'
                    f'\nSu nombre de usuario, en caso de que lo haya olvidado: 20.404.729-4\n'
                    '¡Gracias por usar nuestro sitio!',
                    'noreply@example.com',
                    [email],
                    fail_silently=False,
                )
                return redirect('password_reset_done')
            except User.DoesNotExist:
                form.add_error('email', 'No existe una cuenta con este correo electrónico')
    else:
        form = PasswordResetForm()

    return render(request, 'password_reset_form.html', {'form': form})

# Confirmación del restablecimiento de contraseña
def password_reset_confirm(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            return render(request, 'invalid_token.html')  # Token expirado

        if request.method == 'POST':
            form = SetPasswordForm(reset_token.user, request.POST)
            if form.is_valid():
                form.save()  # Actualizar la contraseña del usuario
                reset_token.delete()  # Eliminar el token después de usarlo
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(reset_token.user)

        return render(request, 'password_reset_confirm.html', {'form': form})
    except PasswordResetToken.DoesNotExist:
        return render(request, 'invalid_token.html')  # Token inválido
    
def password_reset_complete(request):
    if request.method == 'POST':
        form = SetNewPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('login')
    else:
        form = SetNewPasswordForm(user=request.user)
    
    return render(request, 'password_reset_complete.html', {'form': form})


def invalid_token(request):
    return render(request, 'invalid_token.html')

def password_reset_done(request):
    return render(request, 'password_reset_done.html')